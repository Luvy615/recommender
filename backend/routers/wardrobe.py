from fastapi import APIRouter, Depends, HTTPException
from typing import List

from backend.models.outfit import Outfit, OutfitCreate
from backend.services.outfit_service import OutfitService

router = APIRouter(prefix="/api/wardrobe", tags=["wardrobe"])


@router.post("/save-outfit", response_model=Outfit)
def save_outfit(outfit_data: OutfitCreate):
    service = OutfitService()
    try:
        outfit = service.create_outfit(outfit_data)
        return outfit
    finally:
        service.close()


@router.get("/{outfit_id}", response_model=Outfit)
def get_outfit(outfit_id: str):
    service = OutfitService()
    try:
        outfit = service.get_outfit(outfit_id)
        if not outfit:
            raise HTTPException(status_code=404, detail="Outfit not found")
        return outfit
    finally:
        service.close()


@router.get("/list/{user_id}", response_model=List[Outfit])
def get_user_outfits(user_id: str, favorites_only: bool = False):
    service = OutfitService()
    try:
        outfits = service.get_user_outfits(user_id, favorites_only)
        return outfits
    finally:
        service.close()


@router.put("/{outfit_id}/favorite", response_model=Outfit)
def toggle_favorite(outfit_id: str):
    service = OutfitService()
    try:
        outfit = service.toggle_favorite(outfit_id)
        if not outfit:
            raise HTTPException(status_code=404, detail="Outfit not found")
        return outfit
    finally:
        service.close()


@router.delete("/{outfit_id}")
def delete_outfit(outfit_id: str):
    service = OutfitService()
    try:
        success = service.delete_outfit(outfit_id)
        if not success:
            raise HTTPException(status_code=404, detail="Outfit not found")
        return {"message": "Outfit deleted successfully"}
    finally:
        service.close()
