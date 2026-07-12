from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.content_analysis import ContentAnalysis
from app.models.product import Product
from app.models.script import Script, ScriptScene
from app.schemas.script import (
    ScriptCreate,
    ScriptResponse,
    ScriptUpdate,
)
from app.security import get_current_user


router = APIRouter(
    prefix="/api/scripts",
    tags=["脚本分镜"],
    dependencies=[
        Depends(get_current_user),
    ],
)


def get_script_or_404(
    script_id: int,
    db: Session,
) -> Script:
    statement = (
        select(Script)
        .options(
            selectinload(Script.scenes)
        )
        .where(Script.id == script_id)
    )

    script = db.scalar(statement)

    if script is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="脚本不存在",
        )

    return script


def validate_references(
    db: Session,
    product_id: int,
    content_analysis_id: int | None,
) -> None:
    product = db.get(
        Product,
        product_id,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联商品不存在",
        )

    if content_analysis_id is None:
        return

    analysis = db.get(
        ContentAnalysis,
        content_analysis_id,
    )

    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联的内容拆解记录不存在",
        )

    if analysis.product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="内容拆解记录与所选商品不一致",
        )


@router.get("")
def get_script_list(
    product_id: int | None = Query(
        default=None,
        gt=0,
    ),
    script_status: str | None = Query(
        default=None,
        alias="status",
    ),
    keyword: str | None = Query(
        default=None,
        max_length=100,
    ),
    db: Session = Depends(get_db),
) -> dict:
    """查询脚本列表。"""

    statement = (
        select(Script)
        .options(
            selectinload(Script.scenes)
        )
    )

    if product_id is not None:
        statement = statement.where(
            Script.product_id == product_id
        )

    if script_status:
        statement = statement.where(
            Script.status == script_status
        )

    if keyword:
        statement = statement.where(
            Script.title.like(
                f"%{keyword.strip()}%"
            )
        )

    statement = statement.order_by(
        Script.updated_at.desc(),
        Script.id.desc(),
    )

    scripts = db.scalars(
        statement
    ).unique().all()

    return {
        "code": 200,
        "message": "查询脚本列表成功",
        "data": [
            ScriptResponse
            .model_validate(script)
            .model_dump()
            for script in scripts
        ],
    }


@router.get("/{script_id}")
def get_script_detail(
    script_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """查询脚本详情。"""

    script = get_script_or_404(
        script_id,
        db,
    )

    return {
        "code": 200,
        "message": "查询脚本详情成功",
        "data": ScriptResponse
        .model_validate(script)
        .model_dump(),
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def create_script(
    create_data: ScriptCreate,
    db: Session = Depends(get_db),
) -> dict:
    """新增脚本及其分镜。"""

    validate_references(
        db=db,
        product_id=create_data.product_id,
        content_analysis_id=(
            create_data.content_analysis_id
        ),
    )

    script_data = create_data.model_dump(
        exclude={"scenes"},
    )

    script = Script(**script_data)

    for scene_data in create_data.scenes:
        script.scenes.append(
            ScriptScene(
                **scene_data.model_dump()
            )
        )

    try:
        db.add(script)
        db.commit()
    except IntegrityError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分镜序号不能重复",
        ) from error

    created_script = get_script_or_404(
        script.id,
        db,
    )

    return {
        "code": 201,
        "message": "脚本创建成功",
        "data": ScriptResponse
        .model_validate(created_script)
        .model_dump(),
    }


@router.put("/{script_id}")
def update_script(
    script_id: int,
    update_data: ScriptUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """修改脚本和分镜。"""

    script = get_script_or_404(
        script_id,
        db,
    )

    update_fields = update_data.model_dump(
        exclude_unset=True,
    )

    scene_fields = update_fields.pop(
        "scenes",
        None,
    )

    final_product_id = update_fields.get(
        "product_id",
        script.product_id,
    )

    final_analysis_id = update_fields.get(
        "content_analysis_id",
        script.content_analysis_id,
    )

    validate_references(
        db=db,
        product_id=final_product_id,
        content_analysis_id=final_analysis_id,
    )

    for field_name, field_value in update_fields.items():
        setattr(
            script,
            field_name,
            field_value,
        )

    if scene_fields is not None:
        script.scenes.clear()

        for scene_data in scene_fields:
            script.scenes.append(
                ScriptScene(**scene_data)
            )

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分镜序号不能重复",
        ) from error

    updated_script = get_script_or_404(
        script_id,
        db,
    )

    return {
        "code": 200,
        "message": "脚本修改成功",
        "data": ScriptResponse
        .model_validate(updated_script)
        .model_dump(),
    }


@router.delete("/{script_id}")
def delete_script(
    script_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """删除脚本及全部分镜。"""

    script = get_script_or_404(
        script_id,
        db,
    )

    db.delete(script)
    db.commit()

    return {
        "code": 200,
        "message": "脚本删除成功",
        "data": None,
    }