import hashlib
from app.utils import int_to_phone, phone_to_int
from typing import Optional

class MinionCracker:
    def __init__(self, hash_val: str, start: str, end: str):
        self.hash_val = hash_val
        self.start = start
        self.end = end

    def crack_range_sync(self) -> Optional[str]:
        """
        Brute-force the MD5 hash over phone numbers with the given prefix and range.
        """
        for i in range(self.start, self.end + 1):
            phone = int_to_phone(i)
            candidate_hash = hashlib.md5(phone.encode()).hexdigest()
            if candidate_hash == self.hash_val:
                return phone
        return None
