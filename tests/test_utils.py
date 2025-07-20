from app.utils import phone_to_int, int_to_phone

def test_phone_to_int_valid():
    assert phone_to_int("050-1234567") == 501234567
    assert phone_to_int("057-0000000") == 570000000

def test_int_to_phone_valid():
    assert int_to_phone(501234567) == "050-1234567"
    assert int_to_phone(570000000) == "057-0000000"

def test_round_trip():
    phone = "052-7654321"
    num = phone_to_int(phone)
    assert int_to_phone(num) == phone

def test_int_to_phone_padding():
    # Make sure leading zeros are preserved (i.e. 050 not 50)
    assert int_to_phone(500000001) == "050-0000001"
    assert int_to_phone(540000000) == "054-0000000"
