from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self) -> list[Product]:
        return list(self.session.scalars(select(Product).order_by(Product.id.desc())).all())

    def get(self, product_id: int) -> Product | None:
        return self.session.get(Product, product_id)

    def add(self, product: Product) -> None:
        self.session.add(product)

    def delete(self, product: Product) -> None:
        self.session.delete(product)

    def flush(self) -> None:
        self.session.flush()
