from datetime import datetime, timezone
from typing import Optional, List

from db.mongo import get_collection
from models.order import OrderRequest, OrderInDb, OrderLine
from utils.models.model_data_type import ObjectId, Decimal128


class RepositoryOrder:
    @staticmethod
    async def create_order(request: OrderRequest, idempotency_key: str | None = None) -> OrderInDb:
        orders = get_collection("orders")
        inventories = get_collection("inventory")

        # compute subtotal
        from decimal import Decimal
        subtotal_dec = Decimal(0)
        for it in request.items:
            subtotal_dec += Decimal(str(it.qty)) * Decimal(str(it.price))

        total_dec = subtotal_dec  # tax calculations omitted for brevity

        order_doc = request.model_dump()
        # store as BSON Decimal128 for DB
        from bson.decimal128 import Decimal128 as BsonDecimal128
        order_doc["subtotal"] = BsonDecimal128(str(subtotal_dec))
        order_doc["total"] = BsonDecimal128(str(total_dec))
        order_doc["status"] = "created"
        order_doc["created_at"] = datetime.now(timezone.utc)
        order_doc["idempotency_key"] = idempotency_key

        # Decrement inventory items with safety checks (no transactions currently)
        from decimal import Decimal
        from bson.decimal128 import Decimal128 as BsonDecimal128
        for item in request.items:
            qty_dec = Decimal(str(item.qty))
            q_bson = BsonDecimal128(str(qty_dec))
            inc_bson = BsonDecimal128(str(-qty_dec))
            res = await inventories.update_one(
                {"store_id": request.store_id, "product_id": item.product_id, "qty": {"$gte": q_bson}},
                {"$inc": {"qty": inc_bson}},
            )
            if res.matched_count == 0:
                raise ValueError(f"Insufficient stock for product {item.product_id}")
        r = await orders.insert_one(order_doc)
        created = await orders.find_one({"_id": r.inserted_id})
        return OrderInDb.model_validate(created)

    @staticmethod
    async def get_by_id(oid: ObjectId) -> Optional[OrderInDb]:
        orders = get_collection("orders")
        doc = await orders.find_one({"_id": oid})
        if not doc:
            return None
        return OrderInDb.model_validate(doc)

    @staticmethod
    async def get_by_idempotency(key: str) -> Optional[OrderInDb]:
        orders = get_collection("orders")
        doc = await orders.find_one({"idempotency_key": key})
        if not doc:
            return None
        return OrderInDb.model_validate(doc)

    @staticmethod
    async def list_orders(
        store_id: Optional[ObjectId] = None,
        user_id: Optional[ObjectId] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[OrderInDb]:
        orders = get_collection("orders")
        
        query = {}
        if store_id:
            query["store_id"] = store_id
        if user_id:
            query["user_id"] = user_id
        if status:
            query["status"] = status
        
        cursor = orders.find(query).sort("created_at", -1).skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            results.append(OrderInDb.model_validate(doc))
        return results

    @staticmethod
    async def update_status(oid: ObjectId, status: str) -> Optional[OrderInDb]:
        orders = get_collection("orders")
        
        valid_statuses = ["created", "confirmed", "preparing", "ready", "completed", "cancelled"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        result = await orders.update_one(
            {"_id": oid},
            {"$set": {"status": status, "updated_at": datetime.now(timezone.utc)}}
        )
        
        if result.matched_count == 0:
            return None
        
        updated = await orders.find_one({"_id": oid})
        return OrderInDb.model_validate(updated)
