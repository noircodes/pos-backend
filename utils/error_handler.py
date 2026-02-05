"""
Error handling decorator for routers to convert repository exceptions to HTTP exceptions.

This decorator reduces boilerplate in router functions while maintaining
clean separation between business logic (ValueError) and HTTP layer (HTTPException).
"""

from functools import wraps
from fastapi import HTTPException
from loguru import logger


def handle_repo_errors(func):
    """
    Decorator to catch repository exceptions and convert them to HTTP exceptions.
    
    Error mappings:
    - ValueError: 400 Bad Request (client error)
    - KeyError: 404 Not Found (resource not found)
    - Exception: 500 Internal Server Error (unexpected errors)
    
    Usage:
        @router.get("/items/{item_id}")
        @handle_repo_errors
        async def get_item(item_id: str):
            return await RepositoryItem.get_by_id(item_id)
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError as e:
            # Business logic error - client should fix their request
            logger.warning(f"ValueError in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except KeyError as e:
            # Resource not found error
            logger.warning(f"KeyError in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            # Unexpected error - server error
            logger.error(f"Exception in {func.__name__}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    return wrapper