from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.jwt import decode_access_token

security = HTTPBearer()

def get_current_user(
	credentials: HTTPAuthorizationCredentials = Depends(security),
):
	
	token = credentials.credentials

	try:
		payload = decode_access_token(token)
	except Exception:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token inválido ou expirado",
			headers={"WWW-Authenticate": "Bearer"},
		)

	return payload
