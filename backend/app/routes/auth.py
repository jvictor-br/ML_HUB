from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models.models import UserCreate, UserResponse, UserInDB
from app.core.database import db
from app.core.security import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user: UserCreate):
    # 1. Verificar se usuário já existe
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # 2. Criar hash da senha
    hashed_password = get_password_hash(user.password)

    # 3. Preparar documento para salvar
    user_in_db = UserInDB(
        **user.dict(),
        hashed_password=hashed_password
    )
    
    # 4. Salvar no Mongo
    new_user = await db.users.insert_one(user_in_db.dict(by_alias=True))
    
    # 5. Retornar usuário criado (o ID vem do resultado do insert)
    created_user = await db.users.find_one({"_id": new_user.inserted_id})
    return created_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Nota: OAuth2PasswordRequestForm espera campos 'username' e 'password'
    # No nosso caso, o 'username' será o email.
    
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}