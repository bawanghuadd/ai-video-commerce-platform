from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.content_analysis import ContentAnalysis
from app.models.product import Product
from app.schemas.content_analysis import (
    ContentAnalysisCreate,
    ContentAnalysisResponse,
    ContentAnalysisUpdate,
)
from app.security import get_current_user


router = APIRouter(
    prefix="/api/content-analyses",
    tags=["爆款内容拆解"],
    dependencies=[Depends(get_current_user)],
)


def check_product_exists(product_id: int, db: Session) -> None:
    """检查关联商品是否存在。"""

    product = db.scalar(
        select(Product).where(Product.id == product_id)
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联商品不存在",
        )


@router.get("")
def get_content_analysis_list(
    product_id: int | None = Query(default=None, gt=0),
    analysis_status: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> dict:
    """查询爆款内容拆解列表。"""

    statement = select(ContentAnalysis)

    if product_id is not None:
        statement = statement.where(
            ContentAnalysis.product_id == product_id
        )

    if analysis_status:
        statement = statement.where(
            ContentAnalysis.status == analysis_status
        )

    statement = statement.order_by(ContentAnalysis.id.desc())

    records = db.scalars(statement).all()

    return {
        "code": 200,
        "message": "查询爆款内容拆解列表成功",
        "data": [
            ContentAnalysisResponse.model_validate(record).model_dump()
            for record in records
        ],
    }


@router.get("/{analysis_id}")
def get_content_analysis_detail(
    analysis_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """查询单条爆款内容拆解记录。"""

    record = db.get(ContentAnalysis, analysis_id)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="爆款内容拆解记录不存在",
        )

    return {
        "code": 200,
        "message": "查询爆款内容拆解详情成功",
        "data": ContentAnalysisResponse.model_validate(record).model_dump(),
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_content_analysis(
    create_data: ContentAnalysisCreate,
    db: Session = Depends(get_db),
) -> dict:
    """新增爆款内容拆解记录。"""

    check_product_exists(create_data.product_id, db)

    record = ContentAnalysis(**create_data.model_dump())

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "code": 201,
        "message": "爆款内容拆解记录创建成功",
        "data": ContentAnalysisResponse.model_validate(record).model_dump(),
    }


@router.put("/{analysis_id}")
def update_content_analysis(
    analysis_id: int,
    update_data: ContentAnalysisUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """修改爆款内容拆解记录。"""

    record = db.get(ContentAnalysis, analysis_id)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="爆款内容拆解记录不存在",
        )

    update_fields = update_data.model_dump(exclude_unset=True)

    if "product_id" in update_fields:
        check_product_exists(update_fields["product_id"], db)

    for field_name, field_value in update_fields.items():
        setattr(record, field_name, field_value)

    db.commit()
    db.refresh(record)

    return {
        "code": 200,
        "message": "爆款内容拆解记录修改成功",
        "data": ContentAnalysisResponse.model_validate(record).model_dump(),
    }


@router.delete("/{analysis_id}")
def delete_content_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """删除爆款内容拆解记录。"""

    record = db.get(ContentAnalysis, analysis_id)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="爆款内容拆解记录不存在",
        )

    db.delete(record)
    db.commit()

    return {
        "code": 200,
        "message": "爆款内容拆解记录删除成功",
        "data": None,
    }