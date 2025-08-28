import re

from fastapi import HTTPException


regex_email = re.compile(
    r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
)

def validate_phone(str_phone: str, min: int = 7, max: int = 14):
    """Function to validate phone number"""

    if not str_phone.isnumeric():
        raise HTTPException(400, "Nomor telepon bukan berupa angka.")
    phone_len = len(str_phone) + 1
    if not min < phone_len < max:
        raise HTTPException(400, f"Panjang nomor telepon antara {min} - {max} angka.")

    return True


def validate_email(str_email: str):
    """Function to validate email"""

    if not re.fullmatch(regex_email, str_email):
        raise HTTPException(
            400,
            "Format email tidak valid. contoh 'jhon.doe@email.com'."
        )

    return True


def validate_password(password: str, min: int = 6, max: int = 24):
    """Function to validate password"""

    if not min <= len(password) <= max:
        raise HTTPException(400, f"Panjang password antara {min} - {max} karakter.")

    return True