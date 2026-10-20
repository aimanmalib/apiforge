# E-Commerce API Example

An illustrative example of the kind of FastAPI code APIForge targets. It is a
curated sample (in-memory storage, no database), not the verbatim output of a
single run — real output depends on your description and the model you use.

## Features
- Product CRUD with filtering and pagination
- Shopping cart management
- Order creation and tracking
- Status management workflow

## Running
```bash
pip install fastapi uvicorn
cd examples/ecommerce
uvicorn main:app --reload
# then open http://127.0.0.1:8000/docs
```

## Endpoints
- `GET /api/v1/products` — List products (filter, search, paginate)
- `POST /api/v1/products` — Create product
- `GET /api/v1/products/{id}` — Get product
- `PUT /api/v1/products/{id}` — Update product
- `DELETE /api/v1/products/{id}` — Delete product
- `GET /api/v1/cart/{user_id}` — Get cart
- `POST /api/v1/cart/{user_id}/items` — Add to cart
- `DELETE /api/v1/cart/{user_id}/items/{product_id}` — Remove from cart
- `POST /api/v1/orders/{user_id}` — Create order
- `GET /api/v1/orders/{user_id}` — List orders
- `GET /api/v1/orders/{user_id}/{order_id}` — Get order
- `PATCH /api/v1/orders/{user_id}/{order_id}/status` — Update status
