import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

API_TOKEN_ADMIN = os.environ["API_TOKEN_ADMIN"]
API_TOKEN_READER = os.environ["API_TOKEN_READER"]
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]

bearer = HTTPBearer(auto_error=False)

def role_de(token: HTTPAuthorizationCredentials | None) -> str:
    if token is not None:
        if token.credentials == API_TOKEN_ADMIN:
            return "admin"
        if token.credentials == API_TOKEN_READER:
            return "lecteur"
    raise HTTPException(status_code=401, detail="Token absent ou inconnu",
                        headers={"WWW-Authenticate": "Bearer"})

def exiger_lecture(token=Depends(bearer)) -> str:
    return role_de(token)

def exiger_admin(token=Depends(bearer)) -> str:
    role = role_de(token)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Action réservée au rôle admin")
    return role