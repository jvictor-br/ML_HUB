import os
import httpx
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.database import db
from app.models.models import StoreInDB, CredentialsInDB
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

ML_APP_ID = os.getenv("ML_APP_ID")
ML_SECRET_KEY = os.getenv("ML_SECRET_KEY")
ML_REDIRECT_URI = os.getenv("ML_REDIRECT_URI")

@router.get("/connect")
async def connect_mercadolivre():
    """Gera link para o ML."""
    auth_url = (
        f"https://auth.mercadolivre.com.br/authorization"
        f"?response_type=code"
        f"&client_id={ML_APP_ID}"
        f"&redirect_uri={ML_REDIRECT_URI}"
    )
    return RedirectResponse(auth_url)

# --- ROTA UNIFICADA (GET) ---
# Se acessar via navegador (GET), mostra o HTML preenchido
@router.get("/process-code", response_class=HTMLResponse)
async def show_process_page(request: Request, code: Optional[str] = ""):
    # Busca usuários para o dropdown
    users_cursor = db.users.find({})
    users_list = await users_cursor.to_list(length=100)
    
    # Renderiza o HTML passando o 'code' que veio na URL (se houver)
    return templates.TemplateResponse(
        "link_ml.html", 
        {
            "request": request, 
            "users": users_list, 
            "code": code if code else "" 
        }
    )

# --- ROTA UNIFICADA (POST) ---
# Se enviar o formulário (POST), processa a lógica
@router.post("/process-code")
async def process_manual_code_post(
    code: str = Form(...), 
    email: str = Form(...)
):
    # 1. Valida usuário
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # 2. Troca Token
    token_url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": ML_APP_ID,
        "client_secret": ML_SECRET_KEY,
        "code": code,
        "redirect_uri": ML_REDIRECT_URI
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=payload)
        
    if response.status_code != 200:
        # Se der erro, retorna JSON (ou poderia renderizar uma pág de erro)
        return {"error": "Falha ao trocar token", "ml_response": response.json()}

    tokens = response.json()
    ml_user_id = str(tokens.get("user_id"))
    
    # 3. Salva Loja
    store_data = StoreInDB(
        owner_id=str(user["_id"]),
        ml_user_id=ml_user_id,
        name=f"Loja ML {ml_user_id}",
        status="active"
    )
    
    await db.stores.update_one(
        {"ml_user_id": ml_user_id}, 
        {"$set": store_data.dict(exclude={"id"})}, 
        upsert=True
    )
    
    # 4. Salva Credenciais
    expires_in_seconds = tokens.get("expires_in", 21600)
    expiration_date = datetime.utcnow() + timedelta(seconds=expires_in_seconds)
    
    cred_data = CredentialsInDB(
        store_id=ml_user_id,
        access_token=tokens.get("access_token"),
        refresh_token=tokens.get("refresh_token"),
        expires_in=expiration_date,
        ml_app_id=ML_APP_ID
    )
    
    await db.credentials.update_one(
        {"store_id": ml_user_id},
        {"$set": cred_data.dict(exclude={"id"})},
        upsert=True
    )

    return {"message": "✅ SUCESSO! Integração concluída.", "loja": ml_user_id, "usuario": email}