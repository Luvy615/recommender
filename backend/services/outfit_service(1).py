from typing import Optional, List
from sqlalchemy.orm import Session
import uuid

from backend.services.database import SavedOutfitModel, SavedOutfitItemModel, SessionLocal
from backend.models.outfit import Outfit, OutfitCreate, OutfitItem


class OutfitService:
    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()

    def create_outfit(self, outfit_data: OutfitCreate) -> Outfit:
        outfit = SavedOutfitModel(
            id=str(uuid.uuid4()),
            user_id=outfit_data.user_id,
            name=outfit_data.name,
            occasion=outfit_data.occasion,
            weather=outfit_data.weather,
            style=outfit_data.style,
            outfit_image=outfit_data.outfit_image,
            is_favorite=outfit_data.is_favorite
        )
        self.db.add(outfit)
        self.db.flush()

        for idx, item_data in enumerate(outfit_data.items):
            item = SavedOutfitItemModel(
                id=str(uuid.uuid4()),
                outfit_id=outfit.id,
                product_id=item_data.product_id,
                product_name=item_data.product_name,
                product_price=item_data.product_price,
                product_image_url=item_data.product_image_url,
                product_url=item_data.product_url,
                sort_order=item_data.sort_order or idx
            )
            self.db.add(item)

        self.db.commit()
        self.db.refresh(outfit)
        return self._to_outfit(outfit)

    def get_outfit(self, outfit_id: str) -> Optional[Outfit]:
        outfit = self.db.query(SavedOutfitModel).filter(SavedOutfitModel.id == outfit_id).first()
        if not outfit:
            return None
        return self._to_outfit(outfit)

    def get_user_outfits(self, user_id: str, favorites_only: bool = False) -> List[Outfit]:
        query = self.db.query(SavedOutfitModel).filter(SavedOutfitModel.user_id == user_id)
        if favorites_only:
            query = query.filter(SavedOutfitModel.is_favorite == True)
        outfits = query.order_by(SavedOutfitModel.created_at.desc()).all()
        return [self._to_outfit(o) for o in outfits]

    def update_outfit(self, outfit_id: str, update_data: dict) -> Optional[Outfit]:
        outfit = self.db.query(SavedOutfitModel).filter(SavedOutfitModel.id == outfit_id).first()
        if not outfit:
            return None
        
        for key, value in update_data.items():
            if hasattr(outfit, key) and value is not None:
                setattr(outfit, key, value)
        
        self.db.commit()
        self.db.refresh(outfit)
        return self._to_outfit(outfit)

    def toggle_favorite(self, outfit_id: str) -> Optional[Outfit]:
        outfit = self.db.query(SavedOutfitModel).filter(SavedOutfitModel.id == outfit_id).first()
        if not outfit:
            return None
        outfit.is_favorite = not outfit.is_favorite
        self.db.commit()
        self.db.refresh(outfit)
        return self._to_outfit(outfit)

    def delete_outfit(self, outfit_id: str) -> bool:
        outfit = self.db.query(SavedOutfitModel).filter(SavedOutfitModel.id == outfit_id).first()
        if not outfit:
            return False
        self.db.delete(outfit)
        self.db.commit()
        return True

    def _to_outfit(self, outfit_model: SavedOutfitModel) -> Outfit:
        items = [self._to_outfit_item(item) for item in outfit_model.items]
        items.sort(key=lambda x: x.sort_order)
        return Outfit(
            id=outfit_model.id,
            user_id=outfit_model.user_id,
            name=outfit_model.name,
            occasion=outfit_model.occasion,
            weather=outfit_model.weather,
            style=outfit_model.style,
            rating=outfit_model.rating,
            is_favorite=outfit_model.is_favorite,
            outfit_image=outfit_model.outfit_image,
            created_at=outfit_model.created_at,
            items=items
        )

    def _to_outfit_item(self, item_model: SavedOutfitItemModel) -> OutfitItem:
        return OutfitItem(
            product_id=item_model.product_id,
            product_name=item_model.product_name,
            product_price=item_model.product_price,
            product_image_url=item_model.product_image_url,
            product_url=item_model.product_url,
            sort_order=item_model.sort_order
        )
