import asyncio
import hashlib
import httpx
from typing import List, Tuple
import logging

# -------- Logging Setup -------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("master")
# --------------------------------

def phone_to_int(phone: str) -> int:
    """
    Converts a phone number string to an integer.

    Args:
        phone (str): Phone number in the format "05X-XXXXXXX".

    Returns:
        int: The numeric representation of the phone number.
    """
    return int(phone.replace("-", ""))

def int_to_phone(i: int) -> str:
    """
    Converts an integer to a phone number string.

    Args:
        i (int): The numeric phone number.

    Returns:
        str: The formatted phone number string.
    """
    s = f"{i:010d}"
    return f"{s[:3]}-{s[3:]}"

def generate_ranges(start: int, end: int, chunks: int) -> List[Tuple[int, int]]:
    """
    Splits a numeric range into approximately equal-sized sub-ranges.

    Args:
        start (int): The beginning of the range.
        end (int): The end of the range.
        chunks (int): The number of sub-ranges to create.

    Returns:
        List[Tuple[int, int]]: A list of (start, end) tuples for each sub-range.
    """
    step = (end - start + 1) // chunks
    ranges = []
    for i in range(chunks):
        chunk_start = start + i * step
        chunk_end = start + (i + 1) * step - 1 if i < chunks - 1 else end
        ranges.append((chunk_start, chunk_end))
    return ranges

async def send_to_minion(port: int, hash_val: str, start: int, end: int):
    """
    Sends a cracking task to a specific Minion service over REST API.

    Args:
        port (int): The port where the Minion is running.
        hash_val (str): The MD5 hash to crack.
        start (int): Start of the phone number range.
        end (int): End of the phone number range.

    Returns:
        str or None: The cracked password if found, otherwise None.
    """
    url = f"http://localhost:{port}/crack"
    data = {
        "hash": hash_val,
        "range_start": int_to_phone(start),
        "range_end": int_to_phone(end)
    }

    try:
        logger.info(f"[MASTER] Sending range {data['range_start']} – {data['range_end']} to minion on port {port}")
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.post(url, json=data)
            res.raise_for_status()
            result = res.json()
            if result.get("found"):
                logger.info(f"[✓] Password found by minion {port}: {result['password']}")
                return result["password"]
            else:
                logger.info(f"[X] Minion {port} completed range without match")

    except Exception as e:
        logger.warning(f"[!] Minion {port} failed for range {start}-{end}: {e}")
    return None

async def main():
    """
    Main coordination function that distributes cracking tasks
    across multiple Minion services.

    - Reads hashes to crack (currently hardcoded)
    - Divides phone ranges between Minions
    - Sends tasks concurrently
    - Prints results
    """
    hashes = [
        hashlib.md5("050-1234567".encode()).hexdigest(),
        hashlib.md5("054-9876543".encode()).hexdigest()
    ]

    minion_ports = [8001, 8002, 8003, 8004]

    for hash_val in hashes:
        logger.info(f"[MASTER] Starting crack for hash {hash_val[:8]}...")
        start = phone_to_int("050-0000000")
        end = phone_to_int("059-9999999")
        ranges = generate_ranges(start, end, len(minion_ports))

        tasks = [
            send_to_minion(minion_ports[i], hash_val, r[0], r[1])
            for i, r in enumerate(ranges)
        ]

        results = await asyncio.gather(*tasks)
        passwords = [p for p in results if p]

        if passwords:
            logger.info(f"[✓] Final cracked password: {passwords[0]}")
        else:
            logger.info(f"[X] No match found for hash {hash_val[:8]}")

if __name__ == "__main__":
    asyncio.run(main())
