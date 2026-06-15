"""
Simple static token authentication dependency for FastAPI.
"""
from __future__ import annotations
from fastapi import Header, HTTPException, status
from typing import Optional

from . import config

def verify_token(authorization: Optional[str] = Header(None)):
    # Accept bare token in header Authorization: 1234 or Authorization: Bearer 1234
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    token = authorization.split()[-1]
    if token != config.AUTH_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return True
