from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    """商品公共字段。"""

    product_name: str = Field(
        min_length=1,
        max_length=100,
        description="商品名称",
    )

    category: str = Field(
        min_length=1,
        max_length=50,
        description="商品分类",
    )

    price: float = Field(
        gt=0,
        description="商品价格，必须大于0",
    )

    stock: int = Field(
        ge=0,
        description="商品库存不能小于0",
    )

    selling_points: str | None = Field(
        default=None,
        max_length=1000,
        description="商品卖点",
    )

    target_audience: str | None = Field(
        default=None,
        max_length=200,
        description="目标人群",
    )


class ProductCreate(ProductBase):
    """新增商品时接收的数据。"""

    pass


class ProductUpdate(BaseModel):
    """修改商品时接收的数据，所有字段均可选。"""

    product_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    price: float | None = Field(
        default=None,
        gt=0,
    )

    stock: int | None = Field(
        default=None,
        ge=0,
    )

    selling_points: str | None = Field(
        default=None,
        max_length=1000,
    )

    target_audience: str | None = Field(
        default=None,
        max_length=200,
    )


class ProductResponse(ProductBase):
    """返回给前端的完整商品数据。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime