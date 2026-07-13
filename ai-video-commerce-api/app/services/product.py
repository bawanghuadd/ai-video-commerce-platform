from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.product import Product
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.base import Service, transactional


class ProductService(Service):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.repository = ProductRepository(session)

    def list_products(self) -> list[Product]:
        return self.repository.list()

    def get_product(self, product_id: int) -> Product:
        product = self.repository.get(product_id)
        if product is None:
            raise NotFoundError("商品不存在")
        return product

    @transactional("商品数据冲突")
    def create_product(self, product_data: ProductCreate) -> Product:
        product = Product(**product_data.model_dump())
        self.repository.add(product)
        self.repository.flush()
        return product

    @transactional("商品数据冲突")
    def update_product(self, product_id: int, product_data: ProductUpdate) -> Product:
        product = self.get_product(product_id)
        for field_name, field_value in product_data.model_dump(exclude_unset=True).items():
            setattr(product, field_name, field_value)
        self.repository.flush()
        return product

    @transactional("商品仍被其他数据引用，无法删除")
    def delete_product(self, product_id: int) -> None:
        self.repository.delete(self.get_product(product_id))
        self.repository.flush()
