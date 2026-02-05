# SKU Generation System

## Overview

The POS Backend now features an automatic SKU generation system with the following capabilities:

- **Automatic SKU Generation**: SKUs are auto-generated when creating new products
- **Category-based Prefixes**: Different categories can have different SKU prefixes stored in database
- **Dynamic Category Management**: Categories are managed via API with full CRUD operations
- **Read-only SKUs**: Generated SKUs are visible to users but cannot be manually edited
- **Regenerate Option**: Users can regenerate a SKU if they don't like the format
- **Combo Endpoint**: Lightweight endpoint for dropdown lists in frontend UIs

## SKU Format

Generated SKUs follow this format:
```
{PREFIX}-{DATE}-{CODE}
```

### Example:
- `FOD-20250205-A3B7` - Food category created on Feb 5, 2025
- `BEV-20250205-X9K2` - Beverage category created on Feb 5, 2025
- `PRD-20250205-M4P1` - Default category created on Feb 5, 2025

### Format Breakdown:
- **PREFIX**: Category prefix (e.g., FOD, BEV, ELEC)
- **DATE**: Creation date in YYYYMMDD format
- **CODE**: 4-character random alphanumeric code

## Category Management

Categories are now stored in the database with the following structure:

```json
{
  "_id": "650a1b2c3d4e5f6789abcd0f",
  "name": "food",
  "display_name": "Food",
  "sku_prefix": "FOD",
  "description": "Food items",
  "active": true,
  "created_at": "2025-02-05T10:00:00Z",
  "updated_at": "2025-02-05T10:00:00Z"
}
```

### Category Fields:
- **name**: Unique identifier (e.g., "food", "beverage")
- **display_name**: Human-readable name for UI (e.g., "Food", "Beverage")
- **sku_prefix**: SKU prefix for this category (max 10 characters)
- **description**: Optional description
- **active**: Status flag for soft deletes

### Default Categories
You need to create categories via API before creating products. Common examples:
- Food → `FOD`
- Beverage → `BEV`
- Electronics → `ELEC`
- Clothing → `CLO`
- Accessories → `ACC`

## API Endpoints

### Category Management Endpoints

#### 1. Get Categories for Dropdown (Combo)
**Endpoint**: `GET /categories/combo`

**Description**: Lightweight endpoint for frontend dropdowns - returns only id, name, and display_name.

**Query Parameters**:
- `active_only` (optional, default: true): Show only active categories

**Response**:
```json
[
  {
    "id": "650a1b2c3d4e5f6789abcd0f",
    "name": "food",
    "display_name": "Food"
  },
  {
    "id": "650a1b2c3d4e5f6789abcd10",
    "name": "beverage",
    "display_name": "Beverage"
  }
]
```

#### 2. List All Categories
**Endpoint**: `GET /categories/`

**Query Parameters**:
- `skip`: Pagination offset (default: 0)
- `limit`: Items per page (default: 100, max: 100)
- `active_only`: Show only active categories (default: false)

**Response**: Returns full category details with pagination.

#### 3. Create Category
**Endpoint**: `POST /categories/`

**Request Body**:
```json
{
  "name": "food",
  "display_name": "Food",
  "sku_prefix": "FOD",
  "description": "Food items"
}
```

**Response**:
```json
{
  "id": "650a1b2c3d4e5f6789abcd0f",
  "name": "food",
  "display_name": "Food",
  "sku_prefix": "FOD",
  "description": "Food items",
  "active": true,
  "created_at": "2025-02-05T10:00:00Z",
  "updated_at": "2025-02-05T10:00:00Z"
}
```

#### 4. Get Category by ID
**Endpoint**: `GET /categories/{category_id}`

#### 5. Update Category
**Endpoint**: `PUT /categories/{category_id}`

**Note**: You can update the SKU prefix, which will affect all future products in this category.

#### 6. Delete Category
**Endpoint**: `DELETE /categories/{category_id}`

**Note**: Soft delete only. Cannot delete if category is used by any products.

### Product Management Endpoints

#### 7. Create Product (with Auto-generated SKU)

**Endpoint**: `POST /products/`

**Request Body**:
```json
{
  "name": "Product Name",
  "price": "100.00",
  "cost": "80.00",
  "unit": "pcs",
  "category_id": "650a1b2c3d4e5f6789abcd0f"
}
```

**Response**:
```json
{
  "id": "650a1b2c3d4e5f6789abcd0f",
  "sku": "FOD-20250205-A3B7",
  "name": "Product Name",
  "price": "100.00",
  "cost": "80.00",
  "unit": "pcs",
  "category_id": "650a1b2c3d4e5f6789abcd0f",
  "created_at": "2025-02-05T10:30:00Z"
}
```

**Note**: The `sku` field is optional. If not provided, it will be auto-generated based on the category's SKU prefix.

#### 8. Create Product (with Custom SKU)

**Endpoint**: `POST /products/`

**Request Body**:
```json
{
  "sku": "CUSTOM-001",
  "name": "Custom SKU Product",
  "price": "150.00",
  "category_id": "650a1b2c3d4e5f6789abcd10"
}
```

**Note**: Custom SKUs can be provided but are not recommended for consistency.

#### 9. Regenerate SKU

**Endpoint**: `POST /products/{sku}/regenerate-sku`

**Description**: Generates a new SKU for an existing product while keeping all other data unchanged.

**Example**:
```
POST /products/FOD-20250205-A3B7/regenerate-sku
```

**Response**:
```json
{
  "id": "650a1b2c3d4e5f6789abcd0f",
  "sku": "FOD-20250205-X9K2",
  "name": "Product Name",
  "price": "100.00",
  "cost": "80.00",
  "unit": "pcs",
  "category_id": "650a1b2c3d4e5f6789abcd0f",
  "created_at": "2025-02-05T10:30:00Z",
  "updated_at": "2025-02-05T11:00:00Z"
}
```

## Usage Examples

### Example 1: Create Categories First

```bash
curl -X POST http://localhost:8000/categories/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "food",
    "display_name": "Food",
    "sku_prefix": "FOD",
    "description": "Food items"
  }'
```

```bash
curl -X POST http://localhost:8000/categories/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "beverage",
    "display_name": "Beverage",
    "sku_prefix": "BEV",
    "description": "Beverages"
  }'
```

### Example 2: Get Categories for Dropdown

```bash
curl http://localhost:8000/categories/combo \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Example 3: Create a Food Product

```bash
curl -X POST http://localhost:8000/products/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nasi Goreng",
    "price": "25.00",
    "cost": "15.00",
    "unit": "plate",
    "category_id": "650a1b2c3d4e5f6789abcd0f"
  }'
```

**Generated SKU**: `FOD-20250205-A3B7`

### Example 4: Create a Beverage Product

```bash
curl -X POST http://localhost:8000/products/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ice Tea",
    "price": "5.00",
    "cost": "2.00",
    "unit": "glass",
    "category_id": "650a1b2c3d4e5f6789abcd10"
  }'
```

**Generated SKU**: `BEV-20250205-X9K2`

### Example 5: Regenerate SKU

```bash
curl -X POST http://localhost:8000/products/FOD-20250205-A3B7/regenerate-sku \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**New SKU**: `FOD-20250205-M4P1`

### Example 6: Update Category SKU Prefix

```bash
curl -X PUT http://localhost:8000/categories/650a1b2c3d4e5f6789abcd0f \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "food",
    "display_name": "Food",
    "sku_prefix": "FOOD",
    "description": "Updated description"
  }'
```

Note: This will not change existing product SKUs, only future ones.

## Features

### Automatic Generation
- SKUs are automatically generated when creating products without providing a SKU
- The system ensures uniqueness by checking for existing SKUs in the database

### Category-based Organization
- Different product categories have different prefixes stored in the database
- Makes it easy to identify product type from SKU
- Categories are managed via dedicated CRUD API endpoints

### Lightweight Combo Endpoint
- Special endpoint `/categories/combo` for frontend dropdowns
- Returns only essential fields (id, name, display_name)
- Sorted by display_name for better UX
- Supports filtering by active status

### Read-Once Generated
- Generated SKUs are visible but cannot be manually edited
- Ensures data consistency and prevents conflicts

### Regenerate Option
- Users can regenerate a SKU if needed
- All product data remains unchanged
- Only the SKU is updated with a new generated value

### Dynamic Prefix Configuration
- Category prefixes are stored in the database
- Admin can create/update/delete categories via API
- Maximum prefix length: 10 characters
- Prefixes are automatically converted to uppercase
- Category validation ensures only valid categories can be used

## Best Practices

1. **Create Categories First**: Always create categories before creating products
2. **Use Categories**: Always provide a category_id for products to get meaningful SKU prefixes
3. **Don't Provide SKU**: Let the system auto-generate SKUs for consistency
4. **Configure Prefixes**: Set up category prefixes that make sense for your business
5. **Use Combo Endpoint**: Use `/categories/combo` for frontend dropdowns
6. **Use Regenerate Sparingly**: Only regenerate SKUs when absolutely necessary

## Error Handling

### SKU Already Exists
```json
{
  "detail": "SKU already exists"
}
```

### Invalid or Inactive Category
```json
{
  "detail": "Invalid or inactive category"
}
```

### Product Not Found
```json
{
  "detail": "Product not found"
}
```

### Invalid Prefix Length
```json
{
  "detail": "SKU prefix must not exceed 10 characters"
}
```

### Category Already Exists
```json
{
  "detail": "Category with name 'food' already exists"
}
```

### Cannot Delete Category with Products
```json
{
  "detail": "Cannot delete category: 5 product(s) reference this category"
}
```

## Migration Notes

If you have existing products with the old string-based category field, you need to:

1. Create categories for each unique category value
2. Update products to reference category IDs instead of strings
3. Update SKU generator code (already done in this version)

## Future Enhancements

Potential improvements for the SKU system:

- Add SKU validation rules per category
- Support multiple prefix formats (e.g., sequential numbering)
- Add SKU search and filtering capabilities
- Bulk SKU regeneration for category updates
- SKU history tracking
- Category hierarchy (parent-child relationships)