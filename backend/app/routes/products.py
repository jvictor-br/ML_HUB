from fastapi import APIRouter, HTTPException
from app.services.product_sync import sync_products_for_store, create_dummy_product

router = APIRouter()

@router.post("/sync/{store_id}")
async def trigger_sync(store_id: str):
    """
    Dispara a sincronização manual dos produtos.
    """
    result = await sync_products_for_store(store_id)
    
    if "error" in result:
        # MUDANÇA AQUI: Passamos o 'result' inteiro no detail, não só a string
        raise HTTPException(status_code=400, detail=result)
        
    return result

@router.get("/")
async def list_local_products():
    """
    (Bônus) Lista o que já temos salvo no MongoDB para conferir.
    """
    from app.core.database import db
    products = await db.products.find({}).to_list(100)
    # Converter _id do Mongo para string para não dar erro no JSON
    for p in products:
        p["_id"] = str(p["_id"])
    return products

@router.post("/create-test/{store_id}")
async def create_test_product_route(store_id: str):
    """
    Cria um parafuso de teste na conta do ML.
    """
    result = await create_dummy_product(store_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
        
    return result