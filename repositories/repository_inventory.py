from datetime import datetime, timezone
from typing import Optional

from db.mongo import get_collection
from models.inventory import InventoryItem
from utils.models.model_data_type import ObjectId, Decimal128


class RepositoryInventory:
    @staticmethod
    async def get_item(store_id: ObjectId, product_id: ObjectId) -> Optional[InventoryItem]:
        coll = get_collection("inventory")
        doc = await coll.find_one({"store_id": store_id, "product_id": product_id})
        if not doc:
            return None
        return InventoryItem.model_validate(doc)

    @staticmethod
    async def adjust_qty(store_id: ObjectId, product_id: ObjectId, delta: Decimal128) -> InventoryItem:
        coll = get_collection("inventory")
        now = datetime.now(timezone.utc)
        # convert to Decimal for comparisons
        from decimal import Decimal
        delta_dec = Decimal(str(delta))
        # Try to update atomic: if no doc exists and delta positive, insert; else update
        if delta_dec >= Decimal(0):
            res = await coll.find_one_and_update(
                {"store_id": store_id, "product_id": product_id},
                {
                    "$inc": {"qty": delta, "version": 1},
                    "$set": {"updated_at": now}
                },
                upsert=True,
                return_document=True
            )
        else:
            # For decrement, ensure sufficient qty
            neg = -delta_dec
            try:
                from bson.decimal128 import Decimal128 as BsonDecimal128
                neg_bson = BsonDecimal128(str(neg))
            except Exception:
                neg_bson = neg
            res = await coll.find_one_and_update(
                {"store_id": store_id, "product_id": product_id, "qty": {"$gte": neg_bson}},
                {
                    "$inc": {"qty": delta, "version": 1},
                    "$set": {"updated_at": now}
                },
                return_document=True
            )
            if not res:
                raise ValueError("Insufficient stock")
        return InventoryItem.model_validate(res)

    @staticmethod
    async def get_by_id(_id: ObjectId) -> Optional[InventoryItem]:
        coll = get_collection("inventory")
        doc = await coll.find_one({"_id": _id})
        if not doc:
            return None
        return InventoryItem.model_validate(doc)
