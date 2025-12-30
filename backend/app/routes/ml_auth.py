import os
import httpx
from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.database import db
from app.models.models import StoreInDB, CredentialsInDB, UserInDB
from app.auth_utils import get_current_active_user
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# --- Constants ---
ML_APP_ID = os.getenv("ML_APP_ID")
ML_SECRET_KEY = os.getenv("ML_SECRET_KEY")
ML_REDIRECT_URI = os.getenv("ML_REDIRECT_URI") # This should point to the n8n webhook
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


class LinkAccountRequest(BaseModel):
    code: str

# --- Helper Function ---
async def exchange_code_for_token(code: str, user_id: str, user_email: str):
    if not ML_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="ML_REDIRECT_URI is not configured.")

    token_url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "authorization_code", "client_id": ML_APP_ID,
        "client_secret": ML_SECRET_KEY, "code": code, "redirect_uri": ML_REDIRECT_URI
    }
    async with httpx.AsyncClient() as client:
        # 1. Exchange code for tokens
        token_response = await client.post(token_url, data=payload)
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Falha ao trocar token: {token_response.json()}")
        
        tokens = token_response.json()
        access_token = tokens.get("access_token")
        ml_user_id = str(tokens.get("user_id"))

        # 2. Fetch user profile from ML to get the store name (nickname)
        store_name = f"Loja ML {ml_user_id}" # Fallback name
        user_info_url = "https://api.mercadolibre.com/users/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_response = await client.get(user_info_url, headers=headers)
        
        if user_info_response.status_code == 200:
            user_info = user_info_response.json()
            store_name = user_info.get("nickname", store_name)

    # 3. Save Store record with the correct name
    store_data = StoreInDB(owner_id=user_id, ml_user_id=ml_user_id, name=store_name, status="active")
    await db.stores.update_one({"ml_user_id": ml_user_id}, {"$set": store_data.dict(exclude={"id"})}, upsert=True)
    
    # 4. Save Credentials
    expires_in = tokens.get("expires_in", 21600)
    cred_data = CredentialsInDB(store_id=ml_user_id, access_token=access_token, refresh_token=tokens.get("refresh_token"), expires_in=datetime.utcnow() + timedelta(seconds=expires_in), ml_app_id=ML_APP_ID)
    await db.credentials.update_one({"store_id": ml_user_id}, {"$set": cred_data.dict(exclude={"id"})}, upsert=True)
    
    return {"message": "Conta do Mercado Livre vinculada com sucesso!", "store_ml_id": ml_user_id}

# --- API Endpoints ---

@router.get("/connect-url")
async def get_connect_url(current_user: UserInDB = Depends(get_current_active_user)):
    """
    [STEP 1 - Called by Frontend]
    Generates the ML authorization URL. No state is needed as per the new user request.
    """
    if not ML_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="ML_REDIRECT_URI is not configured.")
    
    auth_url = (
        f"https://auth.mercadolivre.com.br/authorization"
        f"?response_type=code&client_id={ML_APP_ID}&redirect_uri={ML_REDIRECT_URI}"
    )
    return {"auth_url": auth_url}

@router.get("/process-code")
async def process_ml_callback(code: str):
    """
    [STEP 2 - Called by n8n]
    Receives the code from n8n and immediately redirects it to the frontend.
    The frontend will then handle the linking.
    """
    # Simply toss the code to the frontend integrations page.
    return RedirectResponse(f"{FRONTEND_URL}/integrations?code={code}")

@router.post("/link-account")
async def link_account(
    request: LinkAccountRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    [STEP 3 - Called by Frontend]
    Receives the code from the frontend and links it to the logged-in user.
    """
    try:
        result = await exchange_code_for_token(
            code=request.code,
            user_id=str(current_user["_id"]),
            user_email=current_user["email"]
        )
        return result
    except HTTPException as e:
        # Re-raise the exception to let FastAPI handle the response
        raise e
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=str(e))

# --- Legacy Manual Fallback ---
# These are no longer the primary flow but are kept for direct/manual use.

@router.get("/connect")
async def legacy_connect():
    if not ML_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="ML_REDIRECT_URI not configured.")
    # This manual connect redirects to the manual process-code page.
    # To make it fully manual, we create a different redirect URI if needed,
    # but for now, it will also go to the new redirector.
    # To keep it simple, we assume manual connect is not the main goal.
    manual_redirect_uri = f"{FRONTEND_URL}/manual-link" # A hypothetical manual frontend route
    auth_url = (
        f"https://auth.mercadolivre.com.br/authorization"
        f"?response_type=code&client_id={ML_APP_ID}&redirect_uri={ML_REDIRECT_URI}"
    )
    return RedirectResponse(auth_url)

@router.post("/process-code")
async def handle_manual_form(request: Request, code: str = Form(...), email: str = Form(...)):
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    try:
        result = await exchange_code_for_token(code, str(user["_id"]), user["email"])
        return templates.TemplateResponse("link_ml.html", {"request": request, "message": f"Sucesso! Loja vinculada."})
    except HTTPException as e:
        return templates.TemplateResponse("link_ml.html", {"request": request, "error": e.detail})
