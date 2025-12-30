from fastapi import APIRouter, HTTPException, Depends
from app.core.database import db
from app.auth_utils import get_current_active_user
from app.models.models import UserInDB
from bson import ObjectId

router = APIRouter()

@router.get("/integrations")
async def get_user_integrations(current_user: UserInDB = Depends(get_current_active_user)):
    """
    Fetches a list of all stores/integrations linked to the current user.
    """
    user_id = str(current_user["_id"])
    stores_cursor = db.stores.find({"owner_id": user_id})
    stores = await stores_cursor.to_list(length=100)
    
    # Convert ObjectId to string for JSON serialization
    for store in stores:
        store["_id"] = str(store["_id"])

    return stores

@router.delete("/integrations/ml/{ml_user_id}")
async def delete_ml_integration(ml_user_id: str, current_user: UserInDB = Depends(get_current_active_user)):
    """
    Deletes a Mercado Livre integration for the current user.
    """
    user_id = str(current_user["_id"])

    # First, find the store to ensure it belongs to the current user
    store_to_delete = await db.stores.find_one({
        "ml_user_id": ml_user_id,
        "owner_id": user_id
    })

    if not store_to_delete:
        raise HTTPException(
            status_code=404,
            detail="Integration not found or you do not have permission to delete it."
        )

    # If ownership is confirmed, proceed with deletion
    # 1. Delete the store record
    await db.stores.delete_one({"_id": ObjectId(store_to_delete["_id"])})
    
    # 2. Delete the associated credentials
    await db.credentials.delete_many({"store_id": ml_user_id})

    return {"message": f"Integration for ML User ID {ml_user_id} has been successfully deleted."}
