from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.security import get_current_user

# router = APIRouter(
#     prefix="/api/products",
#     tags=["商品管理"],
# )
router = APIRouter(
    prefix="/api/products",
    tags=["商品管理"],
    dependencies=[
        Depends(get_current_user),
    ],
)

@router.get("")
def get_product_list(
    db: Session = Depends(get_db),
) -> dict:
    """查询全部商品。"""

    statement = select(Product).order_by(Product.id.desc())
    products = db.scalars(statement).all()

    return {
        "code": 200,
        "message": "查询商品列表成功",
        "data": [
            ProductResponse.model_validate(product)
            for product in products
        ],
    }


@router.get("/{product_id}")
def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """查询单个商品。"""

    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在",
        )

    return {
        "code": 200,
        "message": "查询商品成功",
        "data": ProductResponse.model_validate(product),
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
) -> dict:
    """新增商品。"""

    product = Product(**product_data.model_dump())

    db.add(product)
    db.commit()
    db.refresh(product)

    return {
        "code": 201,
        "message": "商品创建成功",
        "data": ProductResponse.model_validate(product),
    }


@router.put("/{product_id}")
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """修改商品。"""

    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在",
        )

    update_data = product_data.model_dump(exclude_unset=True)

    for field_name, field_value in update_data.items():
        setattr(product, field_name, field_value)

    db.commit()
    db.refresh(product)

    return {
        "code": 200,
        "message": "商品修改成功",
        "data": ProductResponse.model_validate(product),
    }


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """删除商品。"""

    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在",
        )

    db.delete(product)
    db.commit()

    return {
        "code": 200,
        "message": "商品删除成功",
        "data": None,
    }