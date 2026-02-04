# POS Backend

[![CI](https://github.com/noircodes/pos-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/noircodes/pos-backend/actions/workflows/ci.yml)

A modern Point of Sale (POS) backend service built with FastAPI and MongoDB.

## Features

### Phase 1 — Core Functionality

- **Authentication & Authorization**
  - JWT-based authentication (register, login)
  - Secure password hashing with bcrypt
  - Role-based access control (admin, user)

- **User Management**
  - Create users with validation
  - User CRUD operations
  - Unique username and email constraints

- **Product Management**
  - Product creation with SKU validation
  - List products with pagination
  - Price and quantity tracking

- **Order Management**
  - Create orders with multiple items
  - Idempotency support for order creation
  - List orders with filters (store_id, user_id, status)
  - Update order status workflow
  - Order status: created → confirmed → preparing → ready → completed (or cancelled)

- **Inventory Management**
  - Adjust inventory quantities
  - Stock validation before order creation
  - Per-store inventory tracking

## Tech Stack

- **Backend Framework**: FastAPI
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT (jsonwebtoken)
- **Password Hashing**: bcrypt
- **Testing**: Pytest with AnyIO for async tests
- **CI/CD**: GitHub Actions

## Project Structure

```
pos-backend/
├── core/                   # Core configuration and security
│   ├── config.py           # Application settings
│   └── security.py         # JWT and password hashing
├── db/                     # Database connection
│   └── mongo.py            # MongoDB client setup
├── models/                 # Pydantic models
│   ├── auth.py             # Auth models (Token, TokenPayload)
│   ├── inventory.py        # Inventory models
│   ├── model_audit.py      # Audit trail mixin
│   ├── model_user.py       # User models
│   ├── order.py            # Order models
│   └── product.py          # Product models
├── repositories/           # Data access layer
│   ├── repository_idempotency.py
│   ├── repository_inventory.py
│   ├── repository_order.py
│   ├── repository_product.py
│   └── repository_user.py
├── routers/                # API endpoints
│   ├── auth.py             # Auth endpoints
│   ├── inventory.py        # Inventory endpoints
│   ├── orders.py           # Order endpoints
│   ├── products.py         # Product endpoints
│   └── users.py            # User endpoints
├── scripts/                # Utility scripts
├── tests/                  # Test suite
├── utils/                  # Utility functions and models
│   └── models/             # Custom BaseModel and types
├── docker-compose.dev.yml   # Docker compose for development
├── main.py                 # Application entry point
└── requirements.txt         # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.13+
- MongoDB 4.4+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/noircodes/pos-backend.git
   cd pos-backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   PROJECT_NAME=POS Backend
   JWT_SECRET_KEY=your-secret-key-change-in-production
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB=pos
   ```

### Running MongoDB

**Using Docker Compose (Recommended):**
```bash
docker-compose -f docker-compose.dev.yml up -d
```

**Or run MongoDB locally:**
```bash
mongod --dbpath /path/to/data
```

### Starting the Server

```bash
uvicorn main:app --reload --port 8000
```

The API documentation will be available at:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## API Usage Examples

### 1. Register a User

```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Alice",
    "email":"alice@example.com",
    "username":"alice",
    "password":"secret",
    "role":"admin"
  }'
```

### 2. Login

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username":"alice",
    "password":"secret"
  }'
```

Save the `access_token` from the response for subsequent requests.

### 3. Create a Product

```bash
curl -X POST "http://127.0.0.1:8000/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "sku":"SKU-001",
    "name":"Coffee",
    "price":"2.50",
    "unit":"cup"
  }'
```

### 4. Adjust Inventory

```bash
curl -X POST "http://127.0.0.1:8000/stores/{STORE_ID}/inventory/adjust" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "product_id":"<PRODUCT_ID>",
    "delta":"10"
  }'
```

### 5. Create an Order

```bash
curl -X POST "http://127.0.0.1:8000/orders/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "store_id":"<STORE_ID>",
    "user_id":"<USER_ID>",
    "items":[{
      "product_id":"<PRODUCT_ID>",
      "qty":"2",
      "price":"2.50"
    }]
  }'
```

### 6. Get Order by ID

```bash
curl -X GET "http://127.0.0.1:8000/orders/<ORDER_ID>" \
  -H "Authorization: Bearer <TOKEN>"
```

### 7. List Orders

```bash
# List all orders
curl -X GET "http://127.0.0.1:8000/orders/" \
  -H "Authorization: Bearer <TOKEN>"

# Filter by store and status
curl -X GET "http://127.0.0.1:8000/orders/?store_id=<STORE_ID>&status=created&skip=0&limit=20" \
  -H "Authorization: Bearer <TOKEN>"
```

### 8. Update Order Status

```bash
curl -X PATCH "http://127.0.0.1:8000/orders/<ORDER_ID>/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "status":"confirmed"
  }'
```

**Valid Order Statuses:**
- `created` - Initial state
- `confirmed` - Order confirmed
- `preparing` - Being prepared
- `ready` - Ready for pickup/delivery
- `completed` - Order completed
- `cancelled` - Order cancelled

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run tests with coverage:

```bash
pytest tests/ --cov=. --cov-report=html
```

**Current Test Coverage:**
- Authentication: Register, Login, Current User
- Products: Create, List
- Inventory: Adjust, Persistence
- Orders: Create, Get by ID, List, Update Status

## Development

### Code Style

This project uses:
- **Pydantic V2** with ConfigDict
- Timezone-aware datetime objects (`datetime.now(timezone.utc)`)
- Custom BaseModel from `utils.models.model_data_type`
- Async/await patterns throughout

### Idempotency

Order creation supports idempotency via the `Idempotency-Key` header:

```bash
curl -X POST "http://127.0.0.1:8000/orders/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Idempotency-Key: unique-key-123" \
  -d '{...}'
```

Repeating the same request with the same idempotency key will return the same order without creating duplicates.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.