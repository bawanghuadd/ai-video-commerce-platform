from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.script import Script, ScriptScene
from app.repositories.content_analysis import ContentAnalysisRepository
from app.repositories.product import ProductRepository
from app.repositories.script import ScriptRepository
from app.schemas.script import ScriptCreate, ScriptUpdate
from app.services.base import Service, transactional


class ScriptService(Service):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.repository = ScriptRepository(session)
        self.products = ProductRepository(session)
        self.analyses = ContentAnalysisRepository(session)

    def _validate_references(
        self,
        product_id: int,
        content_analysis_id: int | None,
    ) -> None:
        if self.products.get(product_id) is None:
            raise NotFoundError("关联商品不存在")
        if content_analysis_id is None:
            return
        analysis = self.analyses.get(content_analysis_id)
        if analysis is None:
            raise NotFoundError("关联的内容拆解记录不存在")
        if analysis.product_id != product_id:
            raise ValidationError("内容拆解记录与所选商品不一致")

    def list_scripts(
        self,
        product_id: int | None = None,
        status: str | None = None,
        keyword: str | None = None,
    ) -> list[Script]:
        return self.repository.list(product_id, status, keyword)

    def get_script(self, script_id: int) -> Script:
        script = self.repository.get(script_id)
        if script is None:
            raise NotFoundError("脚本不存在")
        return script

    @transactional("分镜序号不能重复")
    def create_script(self, create_data: ScriptCreate) -> Script:
        self._validate_references(create_data.product_id, create_data.content_analysis_id)
        script = Script(**create_data.model_dump(exclude={"scenes"}))
        script.scenes.extend(
            ScriptScene(**scene.model_dump()) for scene in create_data.scenes
        )
        self.repository.add(script)
        self.repository.flush()
        return script

    @transactional("分镜序号不能重复")
    def update_script(self, script_id: int, update_data: ScriptUpdate) -> Script:
        script = self.get_script(script_id)
        fields = update_data.model_dump(exclude_unset=True)
        scenes = fields.pop("scenes", None)
        product_id = fields.get("product_id", script.product_id)
        analysis_id = fields.get("content_analysis_id", script.content_analysis_id)
        self._validate_references(product_id, analysis_id)
        for field_name, field_value in fields.items():
            setattr(script, field_name, field_value)
        if scenes is not None:
            self.repository.replace_scenes(script, scenes)
        self.repository.flush()
        return script

    @transactional("脚本仍被视频任务引用，无法删除")
    def delete_script(self, script_id: int) -> None:
        self.repository.delete(self.get_script(script_id))
        self.repository.flush()
