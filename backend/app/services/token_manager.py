import os
import httpx
from datetime import datetime, timedelta
from app.core.database import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TokenManager")

ML_APP_ID = os.getenv("ML_APP_ID")
ML_SECRET_KEY = os.getenv("ML_SECRET_KEY")

async def refresh_expiring_tokens():
    logger.info("🕒 Verificando tokens próximos da expiração...")
    limit_time = datetime.utcnow() + timedelta(minutes=60)
    cursor = db.credentials.find({"expires_in": {"$lt": limit_time}})
    
    async for cred in cursor:
        store_id = cred.get("store_id")
        refresh_token = cred.get("refresh_token")
        
        logger.info(f"🔄 Renovando token da loja {store_id}...")
        url = "https://api.mercadolibre.com/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": ML_APP_ID,
            "client_secret": ML_SECRET_KEY,
            "refresh_token": refresh_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            
        if response.status_code == 200:
            new_tokens = response.json()
            expires_in_seconds = new_tokens.get("expires_in", 21600)
            new_expiration = datetime.utcnow() + timedelta(seconds=expires_in_seconds)
            await db.credentials.update_one(
                {"_id": cred["_id"]},
                {"$set": {
                    "access_token": new_tokens["access_token"],
                    "refresh_token": new_tokens["refresh_token"],
                    "expires_in": new_expiration
                }}
            )
            logger.info(f"✅ Token da loja {store_id} renovado com sucesso!")
            
        else:
            logger.error(f"❌ Falha ao renovar loja {store_id}: {response.text}")