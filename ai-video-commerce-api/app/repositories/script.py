from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.script import Script, ScriptScene


class ScriptRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(
        self,
        product_id: int | None = None,
        status: str | None = None,
        keyword: str | None = None,
    ) -> list[Script]:
        statement = select(Script).options(selectinload(Script.scenes))
        if product_id is not None:
            statement = statement.where(Script.product_id == product_id)
        if status:
            statement = statement.where(Script.status == status)
        if keyword:
            statement = statement.where(Script.title.like(f"%{keyword.strip()}%"))
        statement = statement.order_by(Script.updated_at.desc(), Script.id.desc())
        return list(self.session.scalars(statement).unique().all())

    def get(self, script_id: int) -> Script | None:
        statement = (
            select(Script)
            .options(selectinload(Script.scenes))
            .where(Script.id == script_id)
        )
        return self.session.scalar(statement)

    def add(self, script: Script) -> None:
        self.session.add(script)

    def delete(self, script: Script) -> None:
        self.session.delete(script)

    def replace_scenes(self, script: Script, scenes: list[dict]) -> None:
        script.scenes.clear()
        self.session.flush()
        script.scenes.extend(ScriptScene(**scene) for scene in scenes)

    def flush(self) -> None:
        self.session.flush()
