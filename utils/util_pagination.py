import json
from fastapi.encoders import jsonable_encoder

from typing import Any, Dict, List, Optional
from loguru import logger
import pymongo

from utils.models.model_pagination import Pagination, PaginationResult, TGenericPaginationModel, QuerySortingOrder
from utils.util_mongodb import TMongoClientSession, TMongoCollection


async def Paginate(
    collection: TMongoCollection,
    query_filter: dict[str, Any],
    params: Pagination,
    resultItemsClass: type[TGenericPaginationModel],
    session: TMongoClientSession | None = None,
    hint: str | None = None,
    filterItem: bool = True,
    explain: bool = False,
    **kwargs: Any
) -> PaginationResult[TGenericPaginationModel]:
    """
    - Http method GET
    - Single sorting field. if one of `sortby` or `order` is null, sorting query ignored
    """
    
    if params.page == 1:
        total = await collection.count_documents(query_filter)
    else:
        total = -1
    offset = params.size * (params.page - 1)
    cursor = collection.find(
        query_filter,
        resultItemsClass.Projection() if filterItem else {},
        skip=offset,
        limit=params.size,
        session=session,
        hint=hint,
        **kwargs
    )
    if (params.sortby is not None) and (len(params.sortby) > 0):
        cursor.sort(params.sortby, pymongo.ASCENDING if params.order == QuerySortingOrder.Ascending else pymongo.DESCENDING)
    items: list[dict[str, Any]] = await cursor.to_list(length=params.size) # type: ignore

    if explain:
        try:
            explained: Any = await cursor.explain()
            logger.data("pagination explain: \n" + json.dumps(jsonable_encoder(explained), indent=2))
        except Exception as err:
            logger.critical("Error process mongo explain")
            logger.critical(str(err))

    return PaginationResult[resultItemsClass](
        sortby=params.sortby,
        size=params.size,
        page=params.page,
        order=params.order,
        total=total,
        items=[resultItemsClass(**item) for item in items]
    )
    
async def Paginate2(
    collection: TMongoCollection,
    params: Pagination,
    resultItemsClass: type[TGenericPaginationModel],
    pipeline: List[Dict[str, Any]],
    projection: Optional[Dict[str, Any]] = None,
    session: TMongoClientSession | None = None,
    **kwargs: Any
) -> PaginationResult[TGenericPaginationModel]:
    """
    Paginate2: Pagination function for MongoDB aggregation pipelines.
    - Supports $lookup, $match, $project, and other aggregation stages.
    - Includes projection support for shaping the output.
    """
    # Calculate skip and limit for pagination
    offset = params.size * (params.page - 1)

    # Add $skip and $limit stages to the pipeline for pagination
    pagination_stages = [
        {"$skip": offset},
        {"$limit": params.size}
    ]

    # Add sorting if sortby and order are provided
    if (params.sortby is not None) and (len(params.sortby) > 0):
        sort_order = pymongo.ASCENDING if params.order == QuerySortingOrder.Ascending else pymongo.DESCENDING
        pipeline.append({"$sort": {params.sortby: sort_order}})

    # Add projection stage if provided
    if projection:
        pipeline.append({"$project": projection})

    # Add pagination stages to the pipeline
    pipeline.extend(pagination_stages)

    # Execute the aggregation pipeline
    cursor = collection.aggregate(pipeline, session=session, **kwargs)

    # Fetch the paginated results
    items: List[Dict[str, Any]] = await cursor.to_list(length=params.size)

    # Count total documents (using the $match stage from the pipeline if available)
    match_stage = next((stage for stage in pipeline if "$match" in stage), {})
    total = await collection.count_documents(match_stage.get("$match", {}))

    # Return the paginated result
    return PaginationResult[TGenericPaginationModel](
        sortby=params.sortby,
        size=params.size,
        page=params.page,
        order=params.order,
        total=total,
        items=[resultItemsClass(**item) for item in items]
    )