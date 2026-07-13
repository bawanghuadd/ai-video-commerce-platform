from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.knowledge import KnowledgeItem
from app.repositories.knowledge import KnowledgeRepository
from app.repositories.product import ProductRepository
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate
from app.services.base import Service, transactional


class KnowledgeService(Service):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.repository = KnowledgeRepository(session)
        self.products = ProductRepository(session)

    def _validate_product(self, product_id: int | None) -> None:
        if product_id is not None and self.products.get(product_id) is None:
            raise NotFoundError("关联商品不存在")

    def list_items(self, **filters) -> list[KnowledgeItem]:
        return self.repository.list(**filters)

    def get_item(self, knowledge_id: int) -> KnowledgeItem:
        item = self.repository.get(knowledge_id)
        if item is None:
            raise NotFoundError("知识库条目不存在")
        return item

    @transactional("知识库数据冲突")
    def create_item(self, create_data: KnowledgeCreate) -> KnowledgeItem:
        self._validate_product(create_data.product_id)
        item = KnowledgeItem(**create_data.model_dump())
        self.repository.add(item)
        self.repository.flush()
        return item

    @transactional("知识库数据冲突")
    def update_item(self, knowledge_id: int, update_data: KnowledgeUpdate) -> KnowledgeItem:
        item = self.get_item(knowledge_id)
        fields = update_data.model_dump(exclude_unset=True)
        if "product_id" in fields:
            self._validate_product(fields["product_id"])
        for field_name, field_value in fields.items():
            setattr(item, field_name, field_value)
        self.repository.flush()
        return item

    @transactional("知识引用次数更新冲突")
    def record_usage(self, knowledge_id: int) -> KnowledgeItem:
        if not self.repository.increment_usage(knowledge_id):
            raise NotFoundError("知识库条目不存在")
        self.repository.flush()
        self.session.expire_all()
        return self.get_item(knowledge_id)

    @transactional("知识库数据冲突")
    def delete_item(self, knowledge_id: int) -> None:
        self.repository.delete(self.get_item(knowledge_id))
        self.repository.flush()
