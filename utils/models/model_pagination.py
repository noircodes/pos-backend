from enum import Enum
from typing import Generic, List, Optional, TypeVar

from fastapi import Body, Query
from pydantic import Field

from utils.models.model_data_type import BaseModel



class QuerySortingOrder(str, Enum):
    Ascending = "asc"
    Descending = "desc"

class Pagination(BaseModel):

    sortby: str | None = Field(
        default=None,
        max_length=50,
        examples=["_id"]
    )
    size: int = Field(
        default=100,
        ge=1,
        le=100,
        description="Jumlah item per halaman"
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Nomor halaman"
    )
    order: QuerySortingOrder = Field(
        default=QuerySortingOrder.Ascending,
        description="Urutan"
    )

    @classmethod
    def QueryParam(
        cls,
        size: int = Query(
            default=10,
            ge=1,
            le=100,
            description="Jumlah item per halaman"
        ),
        page: int = Query(
            default=1,
            ge=1,
            description="Nomor halaman"
        ),
        sortby: str | None = Query(
            default=None,
            max_length=50,
            description="Urutkan berdasarkan nama kolom"
        ),
        order: QuerySortingOrder = Query(
            default=QuerySortingOrder.Ascending,
            description="Urutan"
        )
    ):
        return cls(
            size=size,
            page=page,
            sortby=sortby,
            order=order
        )
    
class PaginationSort(BaseModel):
    sortby: str = Field(
        default=...,
        max_length=50,
        description="Urutkan berdasarkan nama kolom",
        examples=["createdTime"]
    )
    order: QuerySortingOrder = Field(
        default=QuerySortingOrder.Ascending,
        description="Urutan"
    )

class Pagination2(BaseModel):
    size: int = Body(
        default=100,
        ge=1,
        le=100
    )
    page: int = Body(
        default=1,
        ge=1,
    )
    sort: Optional[List[PaginationSort]] = Body(
        default=None,
        title="Sort"
    )

    @classmethod
    def QueryParam(
        cls,
        size: int = Body(
            default=10,
            ge=1,
            le=100,
            description="Jumlah item per halaman"
        ),
        page: int = Body(
            default=1,
            ge=1,
            description="Page number"
        ),
        sort: Optional[List[PaginationSort]] = Body(
            default=None,
            title="Sort",
            description="Array urutan nama kolom"
        )
    ):
        return cls(
            sort=sort,
            size=size,
            page=page
        )
    
TGenericPaginationModel = TypeVar("TGenericPaginationModel", bound=BaseModel) # must derived from BaseModel
    
class PaginationResult(BaseModel, Generic[TGenericPaginationModel]):

    size: int = Field(
        default=...,
        description="Jumlah item per halaman",
        examples=[100]
    )
    page: int = Field(
        default=...,
        description="Nomor halaman",
        examples=[1]
    )
    sortby: Optional[str] = Field(
        default=None,
        description="Urutkan berdasarkan nama kolom",
        examples=["_id"]
    )
    order: QuerySortingOrder = Field(
        default=QuerySortingOrder.Ascending,
        description="Urutan",
        examples=[QuerySortingOrder.Ascending]
    )
    total: int = Field(
        default=...,
        description="Total item.\n**Total hanya dikalkulasi jika `page` bernilai `1`.\nJika `page` bernilai lebih dari `1`, maka nilai `Total` akan selalu `-1`**",
        examples=[10]
    )
    items: List[TGenericPaginationModel] = Field(
        default=...,
        description="Daftar item"
    )

class PaginationResult2(BaseModel, Generic[TGenericPaginationModel]):

    sort: Optional[List[PaginationSort]] = Field(
        default=None,
        title="Sort",
        description="Array urutan nama kolom"
    )
    size: int = Field(
        default=...,
        description="Jumlah item per halaman",
        examples=[100]
    )
    page: int = Field(
        default=...,
        description="Nomor halaman",
        examples=[1]
    )
    total: int = Field(
        default=...,
        description="Total item. **Total hanya dikalkulasi jika `page` bernilai `1`. Jika `page` bernilai lebih dari `1`, maka nilai `Total` akan selalu `-1`**",
        examples=[10]
    )
    items: List[TGenericPaginationModel] = Field(
        default=...,
        description="Daftar item"
    )

