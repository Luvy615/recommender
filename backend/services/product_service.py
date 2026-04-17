from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
import uuid

from backend.services.database import ProductModel, SessionLocal
from backend.models.product import Product, ProductSearch


class ProductService:
    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()

    def create_product(self, product_data: dict) -> Product:
        product = ProductModel(
            id=str(uuid.uuid4()),
            source=product_data.get("source"),
            source_id=product_data.get("source_id", ""),
            name=product_data.get("name", ""),
            category=product_data.get("category"),
            sub_category=product_data.get("sub_category"),
            color=product_data.get("color"),
            style=product_data.get("style"),
            season=product_data.get("season"),
            price=product_data.get("price"),
            image_url=product_data.get("image_url"),
            product_url=product_data.get("product_url")
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return self._to_product(product)

    def get_product(self, product_id: str) -> Optional[Product]:
        product = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            return None
        return self._to_product(product)

    def search_products(self, search: ProductSearch) -> List[Product]:
        query = self.db.query(ProductModel)

        if search.category:
            query = query.filter(ProductModel.category == search.category)
        if search.color:
            query = query.filter(ProductModel.color == search.color)
        if search.style:
            query = query.filter(ProductModel.style == search.style)
        if search.season:
            query = query.filter(ProductModel.season == search.season)
        if search.min_price is not None:
            query = query.filter(ProductModel.price >= search.min_price)
        if search.max_price is not None:
            query = query.filter(ProductModel.price <= search.max_price)
        if search.keyword:
            query = query.filter(
                or_(
                    ProductModel.name.contains(search.keyword),
                    ProductModel.sub_category.contains(search.keyword)
                )
            )

        products = query.limit(search.limit).all()
        return [self._to_product(p) for p in products]

    def search_by_keywords(self, keyword: str, limit: int = 20) -> List[Product]:
        products = self.db.query(ProductModel).filter(
            or_(
                ProductModel.name.contains(keyword),
                ProductModel.category.contains(keyword),
                ProductModel.sub_category.contains(keyword),
                ProductModel.color.contains(keyword),
                ProductModel.style.contains(keyword)
            )
        ).limit(limit).all()
        return [self._to_product(p) for p in products]

    def get_products_by_category(self, category: str, limit: int = 20) -> List[Product]:
        products = self.db.query(ProductModel).filter(
            ProductModel.category == category
        ).limit(limit).all()
        return [self._to_product(p) for p in products]

    def count_products(self) -> int:
        return self.db.query(ProductModel).count()

    def _to_product(self, product_model: ProductModel) -> Product:
        return Product(
            id=product_model.id,
            source=product_model.source,
            source_id=product_model.source_id,
            name=product_model.name,
            category=product_model.category,
            sub_category=product_model.sub_category,
            color=product_model.color,
            style=product_model.style,
            season=product_model.season,
            price=product_model.price,
            image_url=product_model.image_url,
            product_url=product_model.product_url,
            created_at=product_model.created_at
        )
