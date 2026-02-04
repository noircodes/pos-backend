# pos-backend

[![CI](https://github.com/noircodes/pos-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/noircodes/pos-backend/actions/workflows/ci.yml) [![codecov](https://codecov.io/gh/noircodes/pos-backend/branch/main/graph/badge.svg?token=PLACEHOLDER)](https://codecov.io/gh/noircodes/pos-backend/branch/main)

Point of Sale Backend Service

## Phase 1 — Auth, Users, Products, Orders, Inventory

This repo now contains initial scaffolding for Phase 1 of the POS backend (FastAPI + MongoDB):

- JWT auth (register, login), password hashing (bcrypt)
- User repository and endpoints
- Product models, repository and endpoints
- Order management with idempotency support
- Inventory management
- App entrypoint at `app/main.py`

Run locally:

1. install dev requirements: `pip install -r requirements.txt`
2. run MongoDB locally
3. start server: `uvicorn main:app --reload --port 8000`

OpenAPI docs: http://127.0.0.1:8000/docs

Quick usage examples:

1) Register user

curl -X POST "http://127.0.0.1:8000/auth/register" -H "Content-Type: application/json" -d \
  '{"name":"Alice","email":"alice@example.com","username":"alice","password":"secret","role":"admin"}'

2) Login

curl -X POST "http://127.0.0.1:8000/auth/login" -H "Content-Type: application/json" -d \
  '{"username":"alice","password":"secret"}'

3) Create product (use Bearer token from login)

curl -X POST "http://127.0.0.1:8000/products/" -H "Content-Type: application/json" -H "Authorization: Bearer <TOKEN>" -d \
  '{"sku":"SKU-001","name":"Coffee","price":"2.50","unit":"cup"}'

4) Adjust inventory for a store

curl -X POST "http://127.0.0.1:8000/stores/{STORE_ID}/inventory/adjust" -H "Content-Type: application/json" -H "Authorization: Bearer <TOKEN>" -d \
  '{"product_id":"PRODUCT_ID","delta":"10"}'

5) Create an order

curl -X POST "http://127.0.0.1:8000/orders/" -H "Content-Type: application/json" -H "Authorization: Bearer <TOKEN>" -d \
  '{"store_id":"STORE_ID","user_id":"USER_ID","items":[{"product_id":"PRODUCT_ID","qty":"2","price":"2.50"}]}'

6) Get order by ID

curl -X GET "http://127.0.0.1:8000/orders/{ORDER_ID}" -H "Authorization: Bearer <TOKEN>"

7) List orders (with optional filters)

curl -X GET "http://127.0.0.1:8000/orders/?store_id=STORE_ID&status=created&skip=0&limit=20" -H "Authorization: Bearer <TOKEN>"

8) Update order status

curl -X PATCH "http://127.0.0.1:8000/orders/{ORDER_ID}/status" -H "Content-Type: application/json" -H "Authorization: Bearer <TOKEN>" -d \
  '{"status":"confirmed"}'

Valid order statuses: created, confirmed, preparing, ready, completed, cancelled

