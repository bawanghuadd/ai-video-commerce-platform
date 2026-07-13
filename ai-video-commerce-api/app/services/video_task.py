from sqlalchemy.orm import Session

from app.constants.video_tasks import VIDEO_TASK_TRANSITIONS
from app.core.exceptions import NotFoundError, ValidationError
from app.models.video_task import VideoTask
from app.repositories.product import ProductRepository
from app.repositories.script import ScriptRepository
from app.repositories.video_task import VideoTaskRepository
from app.schemas.video_task import VideoTaskCreate, VideoTaskUpdate
from app.services.base import Service, transactional


class VideoTaskService(Service):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.repository = VideoTaskRepository(session)
        self.products = ProductRepository(session)
        self.scripts = ScriptRepository(session)

    def _validate_references(self, product_id: int, script_id: int) -> None:
        if self.products.get(product_id) is None:
            raise NotFoundError("关联商品不存在")
        script = self.scripts.get(script_id)
        if script is None:
            raise NotFoundError("关联脚本不存在")
        if script.product_id != product_id:
            raise ValidationError("所选脚本与商品不一致")

    @staticmethod
    def _validate_transition(current: str, target: str) -> None:
        if current != target and target not in VIDEO_TASK_TRANSITIONS.get(current, set()):
            raise ValidationError(f"视频任务状态不能从“{current}”变更为“{target}”")

    def list_tasks(self, **filters) -> list[VideoTask]:
        return self.repository.list(**filters)

    def get_task(self, task_id: int) -> VideoTask:
        task = self.repository.get(task_id)
        if task is None:
            raise NotFoundError("视频任务不存在")
        return task

    @transactional("视频任务数据冲突")
    def create_task(self, create_data: VideoTaskCreate) -> VideoTask:
        self._validate_references(create_data.product_id, create_data.script_id)
        task = VideoTask(**create_data.model_dump())
        self.repository.add(task)
        self.repository.flush()
        return task

    @transactional("视频任务数据冲突")
    def update_task(self, task_id: int, update_data: VideoTaskUpdate) -> VideoTask:
        task = self.get_task(task_id)
        fields = update_data.model_dump(exclude_unset=True)
        product_id = fields.get("product_id", task.product_id)
        script_id = fields.get("script_id", task.script_id)
        self._validate_references(product_id, script_id)
        if "status" in fields and fields["status"] is not None:
            self._validate_transition(task.status, fields["status"])
        for field_name, field_value in fields.items():
            setattr(task, field_name, field_value)
        self.repository.flush()
        return task

    @transactional("视频任务数据冲突")
    def delete_task(self, task_id: int) -> None:
        self.repository.delete(self.get_task(task_id))
        self.repository.flush()
