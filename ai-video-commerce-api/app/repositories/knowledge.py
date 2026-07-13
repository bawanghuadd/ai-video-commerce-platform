from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeItem


class KnowledgeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(
        self,
        keyword: str | None = None,
        category: str | None = None,
        status: str | None = None,
        product_id: int | None = None,
        is_featured: bool | None = None,
    ) -> list[KnowledgeItem]:
        statement = select(KnowledgeItem)
        if keyword:
            pattern = f"%{keyword.strip()}%"
            statement = statement.where(
                or_(
                    KnowledgeItem.title.like(pattern),
                    KnowledgeItem.summary.like(pattern),
                    KnowledgeItem.content.like(pattern),
                )
            )
        if category:
            statement = statement.where(KnowledgeItem.category == category)
        if status:
            statement = statement.where(KnowledgeItem.status == status)
        if product_id is not None:
            statement = statement.where(KnowledgeItem.product_id == product_id)
        if is_featured is not None:
            statement = statement.where(KnowledgeItem.is_featured == is_featured)
        statement = statement.order_by(
            KnowledgeItem.is_featured.desc(),
            KnowledgeItem.updated_at.desc(),
            KnowledgeItem.id.desc(),
        )
        return list(self.session.scalars(statement).all())

    def get(self, knowledge_id: int) -> KnowledgeItem | None:
        return self.session.get(KnowledgeItem, knowledge_id)

    def add(self, item: KnowledgeItem) -> None:
        self.session.add(item)

    def delete(self, item: KnowledgeItem) -> None:
        self.session.delete(item)

    def increment_usage(self, knowledge_id: int) -> bool:
        result = self.session.execute(
            update(KnowledgeItem)
            .where(KnowledgeItem.id == knowledge_id)
            .values(usage_count=KnowledgeItem.usage_count + 1)
        )
        return bool(result.rowcount)

    def flush(self) -> None:
        self.session.flush()
