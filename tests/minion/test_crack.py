import hashlib
from app.minion.minion_service import MinionCracker
from app.utils import phone_to_int

def test_crack_finds_correct_phone():
    phone = "050-0000001"
    hash_val = hashlib.md5(phone.encode()).hexdigest()
    i = phone_to_int(phone)

    result = MinionCracker({hash_val}, i, i).crack_range_sync()
    assert result == {hash_val: phone}

def test_crack_returns_empty_dict_for_wrong_hash():
    hash_val = hashlib.md5(b"some_other_phone").hexdigest()
    r_start = phone_to_int("050-0000000")
    r_end = phone_to_int("050-0000005")

    result = MinionCracker({hash_val}, r_start, r_end).crack_range_sync()
    assert result == {}

def test_crack_empty_range():
    result = MinionCracker({"irrelevant"}, 10, 5).crack_range_sync()
    assert result == {}

def test_crack_multiple_hashes_finds_only_matches():
    p1 = "050-0000001"
    p2 = "050-0000002"
    h1 = hashlib.md5(p1.encode()).hexdigest()
    h2 = hashlib.md5(p2.encode()).hexdigest()
    h_wrong = hashlib.md5(b"notarealphone").hexdigest()
    r_start = phone_to_int("050-0000000")
    r_end = phone_to_int("050-0000010")

    result = MinionCracker({h1, h2, h_wrong}, r_start, r_end).crack_range_sync()
    assert result == {
        h1: p1,
        h2: p2
    }
