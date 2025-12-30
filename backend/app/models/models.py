from pydantic import BaseModel, EmailStr, Field, BeforeValidator
from typing import Optional, Annotated
from datetime import datetime
PyObjectId = Annotated[str, BeforeValidator(str)]

# ==========================================
# 1. USUÁRIO (User)
# ==========================================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str
    email: EmailStr

class UserInDB(UserResponse):
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)


# ==========================================
# 2. LOJA (Store)
# ==========================================

class StoreCreate(BaseModel):
    name: str

class StoreInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    owner_id: str
    ml_user_id: str 
    name: str
    status: str = "active" 
    created_at: datetime = Field(default_factory=datetime.now)


# ==========================================
# 3. CREDENCIAIS (Credentials)
# ==========================================

class CredentialsInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    store_id: str
    access_token: str
    refresh_token: str
    expires_in: datetime
    ml_app_id: str

# ==========================================
# 4. PRODUTOS
# ==========================================


class ProductInDB(BaseModel):
    ml_id: str             # ID do ML (MLB12345)
    store_id: str          # Dono do produto (ID da Loja)
    title: str
    price: float
    currency_id: str       # BRL
    available_quantity: int
    sold_quantity: int
    permalink: str         # Link do anúncio
    thumbnail: str         # Foto pequena
    status: str            # active, paused, closed
    updated_at: datetime = datetime.utcnow()