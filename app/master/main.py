import asyncio
import httpx
from typing import List, Tuple
import logging
from dotenv import load_dotenv
import os
from app.utils import phone_to_int, int_to_phone ##step 2
from app.models.CrackRequest import CrackRequest

load_dotenv(dotenv_path="app/master/.env")

# -------- Logging Setup -------- #
logging.basicConfig( ## כאשר אני מפקיד למחלקות להשאיר את זה בmain
    level=logging.INFO,
    format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s"
)
RANGE_SIZE = int(os.getenv("CHUNK_SIZE", "1000000"))


# -------- Master -------- #
class Master:
    def __init__(self, minion_ports: List[int], input_file: str, output_file: str):
        """
        Initialize the master service with list of minion ports,
        input file containing hashes, and output file to write results.
        """
        self.minion_ports = minion_ports
        self.input_file = input_file
        self.output_file = output_file
        self.queue = asyncio.Queue()
        self.results = []
        self.all_hashes = set()
        self.found_hashes = set()
        self.found_hashes_lock = asyncio.Lock()
        self.start = phone_to_int("050-0000000")
        self.end = phone_to_int("059-9999999")
        self.current_minion_index = 0
        self.logger = logging.getLogger("MASTER")

    def get_next_minion(self) -> int:
        """
        Return the next minion port using Round Robin strategy.
        """
        port = self.minion_ports[self.current_minion_index]
        self.current_minion_index = (self.current_minion_index + 1) % len(self.minion_ports)
        return port

    async def load_hashes(self):
        """
        Load all hashes from file into a set, and enqueue only the phone number ranges.
        """
        try:
            with open(self.input_file, "r") as f:
                for line in f:
                    hash_val = line.strip()
                    if hash_val:
                        self.all_hashes.add(hash_val)

            num_ranges = ((self.end - self.start) // RANGE_SIZE) + 1
            ranges = self.generate_ranges(self.start, self.end, num_ranges)

            for r_start, r_end in ranges:
                await self.queue.put((r_start, r_end))

            self.logger.info(f"Loaded {len(self.all_hashes)} hashes from {self.input_file}")
        except FileNotFoundError:
            self.logger.error(f"Input file not found: {self.input_file}")


    def generate_ranges(self, start: int, end: int, chunks: int) -> List[Tuple[int, int]]:
        """
        Split the full phone range into smaller chunks (ranges) based on number of minions.
        """
        step = (end - start + 1) // chunks
        ranges = []
        for i in range(chunks):
            chunk_start = start + i * step
            chunk_end = start + (i + 1) * step - 1 if i < chunks - 1 else end
            ranges.append((chunk_start, chunk_end))
        return ranges

    async def send_to_minion(self, port: int, hashes: List[str], r_start: int, r_end: int) -> dict:
        """
        Send a list of hashes and a range to a minion. Return a dict of found matches: hash → phone.
        """
        url = f"http://localhost:{port}/crack"

        crack_req = CrackRequest(
            hashes=hashes,
            range_start=r_start,
            range_end=r_end
        )

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                res = await client.post(url, json=crack_req.model_dump())
                res.raise_for_status()
                return res.json()
        except Exception as e:
            self.logger.warning(f"[!] Minion {port} failed: {e}")
            return {}

    async def worker(self, worker_id: int):
        """
        Asynchronous worker that continuously:
        - Retrieves a phone number range from the queue
        - Sends the current list of uncracked hashes and the range to an available Minion
        - Processes the result (a dictionary of matched hashes to phone numbers)
        - Adds cracked results to the result list and marks hashes as found
        - Retries the task in case of failure
        - Stops if there are no more hashes left to crack
        """
        while True:
            try:
                r_start, r_end = await self.queue.get()

                async with self.found_hashes_lock:
                    hashes_to_send = list(self.all_hashes - self.found_hashes)

                if not hashes_to_send:
                    self.queue.task_done()
                    while not self.queue.empty():
                        try:
                            self.queue.get_nowait()
                            self.queue.task_done()
                        except asyncio.QueueEmpty:
                            break
                        
                    return

                port = self.get_next_minion()
                self.logger.info(f"[Worker-{worker_id}] Sending {len(hashes_to_send)} hashes to Minion {port} | Range {int_to_phone(r_start)} - {int_to_phone(r_end)}")

                matches = await self.send_to_minion(port, hashes_to_send, r_start, r_end)

                async with self.found_hashes_lock:
                    for h, phone in matches.items():
                        if h not in self.found_hashes:
                            result = f"{h} -> {phone}"
                            self.results.append(result)
                            self.found_hashes.add(h)
                            self.logger.info(f"[Worker-{worker_id}] [✓] Cracked: {result}")

            except Exception as e:
                self.logger.warning(f"[Worker-{worker_id}] Error: {e}")
                await self.queue.put((r_start, r_end))
            finally:
                self.queue.task_done()


    async def run(self):
        """
        Run the master process:
        - Load hashes and ranges into the queue
        - Spawn async workers
        - Wait for all tasks to complete
        - Save results to output file
        """
        await self.load_hashes()
        tasks = [asyncio.create_task(self.worker(i)) for i in range(len(self.minion_ports))]
        await self.queue.join()
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

        with open(self.output_file, "w") as f:
            for line in self.results:
                f.write(line + "\n")
        self.logger.info(f"Results saved to {self.output_file}")

if __name__ == "__main__":
    master = Master(
        minion_ports = os.getenv("MINION_PORTS").split(","),
        input_file = os.getenv("INPUT_FILE", "input.txt"),
        output_file = os.getenv("OUTPUT_FILE", "results.txt")
    )
    asyncio.run(master.run())
