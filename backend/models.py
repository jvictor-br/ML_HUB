from pydantic import BaseModel, EmailStr, Field, BeforeValidator
from typing import Optional, Annotated
from datetime import datetime

# Helper para lidar com o _id do MongoDB (converte ObjectId para string)
PyObjectId = Annotated[str, BeforeValidator(str)]

# ==========================================
# 1. USUÁRIO (User)
# ==========================================

# O que recebemos no cadastro
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=6)

# O que retornamos para o Frontend (Sem senha!)
class UserResponse(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str
    email: EmailStr
    
# O que salvamos no Banco (Com hash de senha)
class UserInDB(UserResponse):
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)


# ==========================================
# 2. LOJA (Store)
# ==========================================

class StoreCreate(BaseModel):
    name: str  # Apelido da loja (ex: "Loja de Tênis")
    # Não pedimos ID do ML aqui pois virá do Callback do OAuth

class StoreInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    owner_id: str  # ID do Usuário dono desta loja
    ml_user_id: str # ID oficial da conta no Mercado Livre
    name: str
    status: str = "active" # active, paused, token_expired
    created_at: datetime = Field(default_factory=datetime.now)


# ==========================================
# 3. CREDENCIAIS (Credentials)
# ==========================================
# Nunca expostas diretamente na API, uso interno

class CredentialsInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    store_id: str # Vincula à Loja (StoreInDB)
    access_token: str
    refresh_token: str
    expires_in: datetime # Data exata de expiração
    ml_app_id: str # App ID usado