from datetime import datetime, timezone, timedelta
from typing import Optional

import bcrypt
from jose import jwt, JWTError

from core.config import settings


def _truncate_password(pw: str) -> str:
    # bcrypt limits passwords to 72 bytes; truncate deterministically on utf-8 bytes
    if pw is None:
        return pw
    b = pw.encode("utf-8")
    if len(b) > 72:
        b = b[:72]
        # decode ignoring partial multi-byte char at the end
        return b.decode("utf-8", "ignore")
    return pw


def hash_password(password: str) -> str:
    pw = _truncate_password(password)
    hashed = bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    plain = _truncate_password(plain)
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise
