from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.video_task import VideoTask


class VideoTaskRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(
        self,
        product_id: int | None = None,
        script_id: int | None = None,
        status: str | None = None,
        keyword: str | None = None,
    ) -> list[VideoTask]:
        statement = select(VideoTask)
        if product_id is not None:
            statement = statement.where(VideoTask.product_id == product_id)
        if script_id is not None:
            statement = statement.where(VideoTask.script_id == script_id)
        if status:
            statement = statement.where(VideoTask.status == status)
        if keyword:
            pattern = f"%{keyword.strip()}%"
            statement = statement.where(
                or_(VideoTask.title.like(pattern), VideoTask.assignee.like(pattern))
            )
        statement = statement.order_by(VideoTask.updated_at.desc(), VideoTask.id.desc())
        return list(self.session.scalars(statement).all())

    def get(self, task_id: int) -> VideoTask | None:
        return self.session.get(VideoTask, task_id)

    def add(self, task: VideoTask) -> None:
        self.session.add(task)

    def delete(self, task: VideoTask) -> None:
        self.session.delete(task)

    def flush(self) -> None:
        self.session.flush()
