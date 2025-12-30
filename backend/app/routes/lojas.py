import httpx
from fastapi import APIRouter, HTTPException, Depends
from app.core.database import db

router = APIRouter()

@router.get("/minha-loja/{ml_user_id}")
async def get_store_info(ml_user_id: str):
    # 1. Busca as credenciais no nosso banco
    cred = await db.credentials.find_one({"store_id": ml_user_id})
    
    if not cred:
        raise HTTPException(status_code=404, detail="Loja não conectada")
    
    access_token = cred["access_token"]
    
    # 2. Pergunta ao Mercado Livre quem é esse usuário
    url = f"https://api.mercadolibre.com/users/{ml_user_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
    if response.status_code != 200:
        return {"error": "Falha ao falar com ML", "ml_response": response.json()}
    
    dados_ml = response.json()
    
    # 3. Retorna os dados bonitinhos
    return {
        "id": dados_ml.get("id"),
        "nome": dados_ml.get("nickname"),
        "link": dados_ml.get("permalink"),
        "cidade": dados_ml.get("address", {}).get("city"),
        "reputacao": dados_ml.get("seller_reputation", {}).get("level_id")
    }