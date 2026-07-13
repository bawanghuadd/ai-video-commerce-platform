from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.common import ApiResponse
from app.schemas.knowledge import KnowledgeCreate, KnowledgeResponse, KnowledgeUpdate
from app.services.knowledge import KnowledgeService


router = APIRouter(
    prefix="/api/knowledge-items",
    tags=["知识库"],
    dependencies=[Depends(get_current_user)],
)


def get_knowledge_service(db: Session = Depends(get_db)) -> KnowledgeService:
    return KnowledgeService(db)


@router.get("", response_model=ApiResponse[list[KnowledgeResponse]])
def get_knowledge_list(
    keyword: str | None = Query(default=None, max_length=100),
    category: str | None = Query(default=None, max_length=50),
    knowledge_status: str | None = Query(default=None, alias="status"),
    product_id: int | None = Query(default=None, gt=0),
    is_featured: bool | None = Query(default=None),
    service: KnowledgeService = Depends(get_knowledge_service),
) -> dict:
    return {
        "code": 200,
        "message": "查询知识库列表成功",
        "data": service.list_items(
            keyword=keyword,
            category=category,
            status=knowledge_status,
            product_id=product_id,
            is_featured=is_featured,
        ),
    }


@router.get("/{knowledge_id}", response_model=ApiResponse[KnowledgeResponse])
def get_knowledge_detail(
    knowledge_id: int,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> dict:
    return {"code": 200, "message": "查询知识库详情成功", "data": service.get_item(knowledge_id)}


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[KnowledgeResponse])
def create_knowledge(
    create_data: KnowledgeCreate,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> dict:
    return {"code": 201, "message": "知识库条目创建成功", "data": service.create_item(create_data)}


@router.put("/{knowledge_id}", response_model=ApiResponse[KnowledgeResponse])
def update_knowledge(
    knowledge_id: int,
    update_data: KnowledgeUpdate,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> dict:
    return {"code": 200, "message": "知识库条目修改成功", "data": service.update_item(knowledge_id, update_data)}


@router.post("/{knowledge_id}/use", response_model=ApiResponse[KnowledgeResponse])
def record_knowledge_usage(
    knowledge_id: int,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> dict:
    return {
        "code": 200,
        "message": "知识引用次数更新成功",
        "data": service.record_usage(knowledge_id),
    }


@router.delete("/{knowledge_id}", response_model=ApiResponse[None])
def delete_knowledge(
    knowledge_id: int,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> dict:
    service.delete_item(knowledge_id)
    return {"code": 200, "message": "知识库条目删除成功", "data": None}