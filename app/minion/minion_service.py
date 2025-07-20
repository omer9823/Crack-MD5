import hashlib
from typing import Dict, Set
from app.utils import int_to_phone
from typing import Optional

class MinionCracker:
    def __init__(self, hashes: Set[str], start: str, end: str):
        self.hashes = hashes
        self.start = start
        self.end = end

    def crack_range_sync(self) -> Dict[str, str]:
        """
        Brute-force the MD5 hash over phone numbers with the given prefix and range.
        """
        found: Dict[str, str] = {}
        for i in range(self.start, self.end + 1):
            phone = int_to_phone(i)
            candidate_hash = hashlib.md5(phone.encode()).hexdigest()
            if candidate_hash in self.hashes:
                found[candidate_hash] = phone
        return found
