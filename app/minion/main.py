from fastapi import FastAPI
import hashlib
from app.minion.models.CrackRequest import CrackRequest
import logging
from app.utils import phone_to_int, int_to_phone

# -------- Logging -------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [MINION] %(message)s"
)
logger = logging.getLogger("minion")
# -------------------------- #

app = FastAPI()

@app.post("/crack")
def crack(req: CrackRequest):
    """
    Attempts to crack the given MD5 hash by brute-forcing all phone numbers
    in the given range (inclusive). If a match is found, the password is returned.

    Args:
        req (CrackRequest): An object containing the hash to crack,
                            and the start and end of the phone number range.

    Returns:
        dict: A dictionary indicating whether the password was found,
              and if so, what the password is.
    """
    logger.info(f"Received range: {req.range_start} – {req.range_end}")
    start = phone_to_int(req.range_start)
    end = phone_to_int(req.range_end)
    target_hash = req.hash.lower()

    for i in range(start, end + 1):
        phone = int_to_phone(i)
        if hashlib.md5(phone.encode()).hexdigest() == target_hash:
            logger.info(f"✓ Match found: {phone}")
            return {"found": True, "password": phone}

    logger.info("X No match in range")
    return {"found": False}