from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError, jwt
from app.core.database import db
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.models import UserInDB

# Define o esquema de autenticação. A URL do token aponta para o endpoint de login.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class TokenData(BaseModel):
    username: str | None = None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """
    Decodifica o token JWT, valida e busca o usuário no banco de dados.
    Esta é a dependência principal que outras dependências de "usuário atual" usarão.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
        
    user = await db.users.find_one({"email": token_data.username})
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """
    Dependência para obter o usuário atual.
    No futuro, pode ser estendida para verificar se o usuário está ativo.
    """
    # Exemplo de verificação de usuário ativo (descomentar se o modelo User tiver 'disabled')
    # if current_user.get("disabled"):
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
