from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.common import ApiResponse
from app.schemas.script import ScriptCreate, ScriptResponse, ScriptUpdate
from app.services.script import ScriptService


router = APIRouter(
    prefix="/api/scripts",
    tags=["脚本分镜"],
    dependencies=[Depends(get_current_user)],
)


def get_script_service(db: Session = Depends(get_db)) -> ScriptService:
    return ScriptService(db)


@router.get("", response_model=ApiResponse[list[ScriptResponse]])
def get_script_list(
    product_id: int | None = Query(default=None, gt=0),
    script_status: str | None = Query(default=None, alias="status"),
    keyword: str | None = Query(default=None, max_length=100),
    service: ScriptService = Depends(get_script_service),
) -> dict:
    return {
        "code": 200,
        "message": "查询脚本列表成功",
        "data": service.list_scripts(product_id, script_status, keyword),
    }


@router.get("/{script_id}", response_model=ApiResponse[ScriptResponse])
def get_script_detail(
    script_id: int,
    service: ScriptService = Depends(get_script_service),
) -> dict:
    return {"code": 200, "message": "查询脚本详情成功", "data": service.get_script(script_id)}


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[ScriptResponse])
def create_script(
    create_data: ScriptCreate,
    service: ScriptService = Depends(get_script_service),
) -> dict:
    return {"code": 201, "message": "脚本创建成功", "data": service.create_script(create_data)}


@router.put("/{script_id}", response_model=ApiResponse[ScriptResponse])
def update_script(
    script_id: int,
    update_data: ScriptUpdate,
    service: ScriptService = Depends(get_script_service),
) -> dict:
    return {"code": 200, "message": "脚本修改成功", "data": service.update_script(script_id, update_data)}


@router.delete("/{script_id}", response_model=ApiResponse[None])
def delete_script(
    script_id: int,
    service: ScriptService = Depends(get_script_service),
) -> dict:
    service.delete_script(script_id)
    return {"code": 200, "message": "脚本删除成功", "data": None}