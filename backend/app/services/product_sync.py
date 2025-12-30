import httpx
from datetime import datetime
from app.core.database import db
from app.models.models import ProductInDB

async def sync_products_for_store(store_id: str):
    """
    Baixa todos os produtos ativos/pausados do ML e salva no Mongo.
    """
    cred = await db.credentials.find_one({"store_id": store_id})
    if not cred:
        return {"error": "Loja não conectada no banco de dados."}
    
    access_token = cred["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        search_url = f"https://api.mercadolibre.com/users/{store_id}/items/search?limit=100"
        
        search_resp = await client.get(search_url, headers=headers)
        if search_resp.status_code != 200:
            return {
                "error": "Falha ao buscar IDs no ML", 
                "status_code": search_resp.status_code,
                "details": search_resp.json()
            }
        
        items_ids = search_resp.json().get("results", [])
        if not items_ids:
            return {"message": "Nenhum produto encontrado nesta loja (Lista Vazia).", "total": 0}
        total_saved = 0
        def chunked(lista, n):
            for i in range(0, len(lista), n):
                yield lista[i:i + n]

        for batch_ids in chunked(items_ids, 20):
            ids_str = ",".join(batch_ids)
            items_url = f"https://api.mercadolibre.com/items?ids={ids_str}"
            
            items_resp = await client.get(items_url, headers=headers)
            items_data = items_resp.json()
            for item_wrapper in items_data:
                item = item_wrapper.get("body")
                status_code = item_wrapper.get("code")
                
                if status_code == 200: 
                    product = ProductInDB(
                        ml_id=item["id"],
                        store_id=str(item["seller_id"]),
                        title=item["title"],
                        price=item["price"],
                        currency_id=item["currency_id"],
                        available_quantity=item["available_quantity"],
                        sold_quantity=item.get("sold_quantity", 0),
                        permalink=item["permalink"],
                        thumbnail=item["thumbnail"],
                        status=item["status"],
                        updated_at=datetime.utcnow()
                    )
                    
                    # Salva (Upsert: se existe, atualiza; se não, cria)
                    await db.products.update_one(
                        {"ml_id": product.ml_id},
                        {"$set": product.dict()},
                        upsert=True
                    )
                    total_saved += 1
        
        return {"message": "Sincronização concluída!", "total_synced": total_saved}
    
# ... (código anterior do sync_products_for_store continua acima)

async def create_dummy_product(store_id: str):
    """
    Cria um anúncio de teste no Mercado Livre para validar a escrita.
    """
    # 1. Recupera o Token
    cred = await db.credentials.find_one({"store_id": store_id})
    if not cred:
        return {"error": "Loja não conectada."}
    
    access_token = cred["access_token"]
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 2. Monta o JSON do Produto (Payload)
    # Categoria MLB271107 = Parafusos (Construção) - Combina com a Fixwell!
    product_payload = {
        "title": "Item De Teste Integração Fixwell - Nao Comprar",
        "category_id": "MLB271107", 
        "price": 999.99, # Preço alto para ninguém comprar
        "currency_id": "BRL",
        "available_quantity": 1,
        "buying_mode": "buy_it_now",
        "listing_type_id": "gold_special", # Clássico (padrão)
        "condition": "new",
        "description": {
            "plain_text": "Este é um anúncio gerado automaticamente via API para teste de integração. Por favor, não compre."
        },
        "pictures": [
            {"source": "https://http2.mlstatic.com/D_NQ_NP_956448-MLA44783353861_022021-O.webp"} # Imagem genérica de parafuso
        ],
        "attributes": [
            {"id": "BRAND", "value_name": "Marca Genérica"},
            {"id": "MODEL", "value_name": "Teste API 1.0"}
        ]
    }
    
    # 3. Envia para o Mercado Livre
    url = "https://api.mercadolibre.com/items"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=product_payload, headers=headers)
        
    if response.status_code != 201: # 201 = Created
        return {
            "error": "Falha ao criar anúncio", 
            "status_code": response.status_code,
            "details": response.json()
        }
    
    # 4. Se deu certo, salva no nosso banco também
    item = response.json()
    
    new_product = ProductInDB(
        ml_id=item["id"],
        store_id=str(item["seller_id"]),
        title=item["title"],
        price=item["price"],
        currency_id=item["currency_id"],
        available_quantity=item["available_quantity"],
        sold_quantity=0,
        permalink=item["permalink"],
        thumbnail=item["pictures"][0]["url"], # Pega a primeira foto
        status=item["status"],
        updated_at=datetime.utcnow()
    )
    
    await db.products.update_one(
        {"ml_id": new_product.ml_id},
        {"$set": new_product.dict()},
        upsert=True
    )

    return {
        "message": "Produto criado com sucesso!", 
        "ml_id": item["id"], 
        "link": item["permalink"]
    }