from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.knowledge import KnowledgeItem
from app.models.product import Product
from app.schemas.knowledge import (
    KnowledgeCreate,
    KnowledgeResponse,
    KnowledgeUpdate,
)
from app.security import get_current_user


router = APIRouter(
    prefix="/api/knowledge-items",
    tags=["知识库"],
    dependencies=[
        Depends(get_current_user),
    ],
)


def get_knowledge_or_404(
    knowledge_id: int,
    db: Session,
) -> KnowledgeItem:
    knowledge_item = db.get(
        KnowledgeItem,
        knowledge_id,
    )

    if knowledge_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库条目不存在",
        )

    return knowledge_item


def validate_product(
    product_id: int | None,
    db: Session,
) -> None:
    if product_id is None:
        return

    product = db.get(
        Product,
        product_id,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联商品不存在",
        )


@router.get("")
def get_knowledge_list(
    keyword: str | None = Query(
        default=None,
        max_length=100,
    ),
    category: str | None = Query(
        default=None,
        max_length=50,
    ),
    knowledge_status: str | None = Query(
        default=None,
        alias="status",
    ),
    product_id: int | None = Query(
        default=None,
        gt=0,
    ),
    is_featured: bool | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
) -> dict:
    """查询知识库列表。"""

    statement = select(KnowledgeItem)

    if keyword:
        search_keyword = (
            f"%{keyword.strip()}%"
        )

        statement = statement.where(
            or_(
                KnowledgeItem.title.like(
                    search_keyword
                ),
                KnowledgeItem.summary.like(
                    search_keyword
                ),
                KnowledgeItem.content.like(
                    search_keyword
                ),
            )
        )

    if category:
        statement = statement.where(
            KnowledgeItem.category == category
        )

    if knowledge_status:
        statement = statement.where(
            KnowledgeItem.status
            == knowledge_status
        )

    if product_id is not None:
        statement = statement.where(
            KnowledgeItem.product_id
            == product_id
        )

    if is_featured is not None:
        statement = statement.where(
            KnowledgeItem.is_featured
            == is_featured
        )

    statement = statement.order_by(
        KnowledgeItem.is_featured.desc(),
        KnowledgeItem.updated_at.desc(),
        KnowledgeItem.id.desc(),
    )

    knowledge_items = db.scalars(
        statement
    ).all()

    return {
        "code": 200,
        "message": "查询知识库列表成功",
        "data": [
            KnowledgeResponse
            .model_validate(item)
            .model_dump()
            for item in knowledge_items
        ],
    }


@router.get("/{knowledge_id}")
def get_knowledge_detail(
    knowledge_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """查询知识库详情。"""

    knowledge_item = get_knowledge_or_404(
        knowledge_id,
        db,
    )

    return {
        "code": 200,
        "message": "查询知识库详情成功",
        "data": KnowledgeResponse
        .model_validate(knowledge_item)
        .model_dump(),
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge(
    create_data: KnowledgeCreate,
    db: Session = Depends(get_db),
) -> dict:
    """新增知识库条目。"""

    validate_product(
        create_data.product_id,
        db,
    )

    knowledge_item = KnowledgeItem(
        **create_data.model_dump()
    )

    db.add(knowledge_item)
    db.commit()
    db.refresh(knowledge_item)

    return {
        "code": 201,
        "message": "知识库条目创建成功",
        "data": KnowledgeResponse
        .model_validate(knowledge_item)
        .model_dump(),
    }


@router.put("/{knowledge_id}")
def update_knowledge(
    knowledge_id: int,
    update_data: KnowledgeUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """修改知识库条目。"""

    knowledge_item = get_knowledge_or_404(
        knowledge_id,
        db,
    )

    update_fields = update_data.model_dump(
        exclude_unset=True,
    )

    if "product_id" in update_fields:
        validate_product(
            update_fields["product_id"],
            db,
        )

    for field_name, field_value in update_fields.items():
        setattr(
            knowledge_item,
            field_name,
            field_value,
        )

    db.commit()
    db.refresh(knowledge_item)

    return {
        "code": 200,
        "message": "知识库条目修改成功",
        "data": KnowledgeResponse
        .model_validate(knowledge_item)
        .model_dump(),
    }


@router.post("/{knowledge_id}/use")
def record_knowledge_usage(
    knowledge_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """记录一次知识引用。"""

    knowledge_item = get_knowledge_or_404(
        knowledge_id,
        db,
    )

    knowledge_item.usage_count += 1

    db.commit()
    db.refresh(knowledge_item)

    return {
        "code": 200,
        "message": "知识引用次数更新成功",
        "data": KnowledgeResponse
        .model_validate(knowledge_item)
        .model_dump(),
    }


@router.delete("/{knowledge_id}")
def delete_knowledge(
    knowledge_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """删除知识库条目。"""

    knowledge_item = get_knowledge_or_404(
        knowledge_id,
        db,
    )

    db.delete(knowledge_item)
    db.commit()

    return {
        "code": 200,
        "message": "知识库条目删除成功",
        "data": None,
    }