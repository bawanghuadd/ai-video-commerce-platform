from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.permissions import require_business_access
from app.schemas.common import ApiResponse
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product import ProductService


router = APIRouter(
    prefix="/api/products",
    tags=["商品管理"],
    dependencies=[Depends(require_business_access)],
)


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)


@router.get("", response_model=ApiResponse[list[ProductResponse]])
def get_product_list(
    service: ProductService = Depends(get_product_service),
) -> dict:
    return {
        "code": 200,
        "message": "查询商品列表成功",
        "data": service.list_products(),
    }


@router.get("/{product_id}", response_model=ApiResponse[ProductResponse])
def get_product_detail(
    product_id: int,
    service: ProductService = Depends(get_product_service),
) -> dict:
    return {
        "code": 200,
        "message": "查询商品成功",
        "data": service.get_product(product_id),
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[ProductResponse],
)
def create_product(
    product_data: ProductCreate,
    service: ProductService = Depends(get_product_service),
) -> dict:
    return {
        "code": 201,
        "message": "商品创建成功",
        "data": service.create_product(product_data),
    }


@router.put("/{product_id}", response_model=ApiResponse[ProductResponse])
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    service: ProductService = Depends(get_product_service),
) -> dict:
    return {
        "code": 200,
        "message": "商品修改成功",
        "data": service.update_product(product_id, product_data),
    }


@router.delete("/{product_id}", response_model=ApiResponse[None])
def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
) -> dict:
    service.delete_product(product_id)
    return {"code": 200, "message": "商品删除成功", "data": None}