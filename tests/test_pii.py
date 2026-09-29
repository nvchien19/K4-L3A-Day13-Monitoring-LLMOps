from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "REDACTED_PHONE_VN" in out


def test_scrub_cccd() -> None:
    out = scrub_text("CCCD 079302012345 của khách hàng")
    assert "079302012345" not in out
    assert "REDACTED_CCCD" in out


def test_scrub_credit_card() -> None:
    card = "4111 1111 1111 1111"
    out = scrub_text(f"Card {card}")
    assert card not in out
    assert "REDACTED_CREDIT_CARD" in out


def test_scrub_passport() -> None:
    out = scrub_text("Passport C1234567 issued in Hanoi")
    assert "C1234567" not in out
    assert "REDACTED_PASSPORT" in out


def test_scrub_vietnamese_address() -> None:
    out = scrub_text("Địa chỉ: 123 Đường Nguyễn Trãi, Quận 1")
    assert "REDACTED_ADDRESS_VN" in out


def test_scrub_vietnamese_full_name() -> None:
    out = scrub_text("Khách hàng Nguyễn Văn An đã đăng ký")
    assert "Nguyễn Văn An" not in out
    assert "REDACTED_VIETNAMESE_NAME" in out
