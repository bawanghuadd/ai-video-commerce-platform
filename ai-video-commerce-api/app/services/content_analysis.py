from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.content_analysis import ContentAnalysis
from app.repositories.content_analysis import ContentAnalysisRepository
from app.repositories.product import ProductRepository
from app.schemas.content_analysis import ContentAnalysisCreate, ContentAnalysisUpdate
from app.services.base import Service, transactional


class ContentAnalysisService(Service):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.repository = ContentAnalysisRepository(session)
        self.products = ProductRepository(session)

    def _ensure_product(self, product_id: int) -> None:
        if self.products.get(product_id) is None:
            raise NotFoundError("关联商品不存在")

    def list_records(
        self,
        product_id: int | None = None,
        status: str | None = None,
    ) -> list[ContentAnalysis]:
        return self.repository.list(product_id, status)

    def get_record(self, analysis_id: int) -> ContentAnalysis:
        record = self.repository.get(analysis_id)
        if record is None:
            raise NotFoundError("爆款内容拆解记录不存在")
        return record

    @transactional("内容拆解数据冲突")
    def create_record(self, create_data: ContentAnalysisCreate) -> ContentAnalysis:
        self._ensure_product(create_data.product_id)
        record = ContentAnalysis(**create_data.model_dump())
        self.repository.add(record)
        self.repository.flush()
        return record

    @transactional("内容拆解数据冲突")
    def update_record(
        self,
        analysis_id: int,
        update_data: ContentAnalysisUpdate,
    ) -> ContentAnalysis:
        record = self.get_record(analysis_id)
        fields = update_data.model_dump(exclude_unset=True)
        if "product_id" in fields:
            self._ensure_product(fields["product_id"])
        for field_name, field_value in fields.items():
            setattr(record, field_name, field_value)
        self.repository.flush()
        return record

    @transactional("内容拆解仍被其他数据引用，无法删除")
    def delete_record(self, analysis_id: int) -> None:
        self.repository.delete(self.get_record(analysis_id))
        self.repository.flush()
