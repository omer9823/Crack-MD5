import hashlib
from app.minion.main import crack_range_sync
from app.utils import phone_to_int

def test_crack_finds_correct_phone():
    phone = "050-0000001"
    hash_val = hashlib.md5(phone.encode()).hexdigest()
    i = phone_to_int(phone)
 
    result = crack_range_sync(hash_val, i, i)
    assert result == phone

def test_crack_returns_none_for_wrong_hash():
    hash_val = hashlib.md5(b"some_other_phone").hexdigest()
    r_start = phone_to_int("050-0000000")
    r_end = phone_to_int("050-0000005")

    result = crack_range_sync(hash_val, r_start, r_end)
    assert result is None

def test_crack_empty_range():
    result = crack_range_sync("irrelevant", 10, 5)
    assert result is None

def test_crack_edge_case():
    phone = "050-0000000"
    hash_val = hashlib.md5(phone.encode()).hexdigest()
    i = phone_to_int(phone)

    result = crack_range_sync(hash_val, i, i)
    assert result == phone
