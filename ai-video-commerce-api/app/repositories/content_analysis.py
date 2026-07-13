from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content_analysis import ContentAnalysis


class ContentAnalysisRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(
        self,
        product_id: int | None = None,
        status: str | None = None,
    ) -> list[ContentAnalysis]:
        statement = select(ContentAnalysis)
        if product_id is not None:
            statement = statement.where(ContentAnalysis.product_id == product_id)
        if status:
            statement = statement.where(ContentAnalysis.status == status)
        statement = statement.order_by(ContentAnalysis.id.desc())
        return list(self.session.scalars(statement).all())

    def get(self, analysis_id: int) -> ContentAnalysis | None:
        return self.session.get(ContentAnalysis, analysis_id)

    def add(self, record: ContentAnalysis) -> None:
        self.session.add(record)

    def delete(self, record: ContentAnalysis) -> None:
        self.session.delete(record)

    def flush(self) -> None:
        self.session.flush()
