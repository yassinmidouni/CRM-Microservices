from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from typing import List, Optional
from datetime import datetime
import httpx
from pydantic import BaseModel, Field
import time
import os

# Constants
MONGO_URI = "mongodb://mongo:27017"
DB_NAME = "crm-project"
CONNECT_TIMEOUT = 10
OPERATION_TIMEOUT = 5

# Order status constants
STATUS_PENDING = "pending"
STATUS_CONFIRMED = "confirmed"
STATUS_PROCESSING = "processing"
STATUS_SHIPPED = "shipped"
STATUS_DELIVERED = "delivered"
STATUS_CANCELLED = "cancelled"

# Prometheus metrics
registry = CollectorRegistry()
order_requests = Counter(
    'order_service_requests_total',
    'Total number of requests to order service',
    ['method', 'endpoint', 'status'],
    registry=registry
)
order_latency = Histogram(
    'order_service_latency_seconds',
    'Time taken to process order requests',
    ['method', 'endpoint'],
    registry=registry
)
order_status_updates = Counter(
    'order_status_updates_total',
    'Total number of order status updates',
    ['from_status', 'to_status'],
    registry=registry
)
active_orders = Gauge(
    'active_orders_total',
    'Total number of active orders',
    registry=registry
)

# Pydantic models
class OrderItem(BaseModel):
    product_id: str = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    quantity: int = Field(..., gt=0, description="Quantity")
    unit_price: float = Field(..., gt=0, description="Unit price")
    subtotal: float = Field(0, description="Subtotal")

class Address(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str
    country: str

class Order(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    customer_id: str
    items: List[OrderItem]
    total_amount: float = 0
    status: str = STATUS_PENDING
    shipping_address: Address
    payment_method: str
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True

class StatusUpdate(BaseModel):
    status: str

# FastAPI app initialization
app = FastAPI(title="Order Service")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
async def get_database():
    client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=CONNECT_TIMEOUT * 1000)
    try:
        await client.admin.command('ping')
        return client[DB_NAME]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# Metrics middleware
async def metrics_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    order_requests.labels(
        request.method,
        request.url.path,
        str(response.status_code)
    ).inc()
    
    order_latency.labels(
        request.method,
        request.url.path
    ).observe(duration)
    
    return response

app.middleware("http")(metrics_middleware)

# Helper functions
async def validate_customer(customer_id: str) -> bool:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"http://customer-service:8085/api/customers/{customer_id}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error validating customer: {e}")
            return False

# Routes
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST
    )

@app.post("/api/orders", response_model=Order)
async def create_order(order: Order, db=Depends(get_database)):
    if not await validate_customer(order.customer_id):
        raise HTTPException(status_code=400, detail="Invalid customer ID")

    # Calculate totals
    total_amount = 0
    for item in order.items:
        item.subtotal = item.quantity * item.unit_price
        total_amount += item.subtotal
    order.total_amount = total_amount

    # Insert order
    order_dict = order.dict(by_alias=True)
    order_dict["created_at"] = datetime.utcnow()
    order_dict["updated_at"] = order_dict["created_at"]
    
    result = await db.orders.insert_one(order_dict)
    order_dict["_id"] = str(result.inserted_id)
    
    active_orders.inc()
    return order_dict

@app.get("/api/orders", response_model=List[Order])
async def get_orders(
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0),
    db=Depends(get_database)
):
    skip = (page - 1) * limit
    filter_query = {}
    if customer_id:
        filter_query["customer_id"] = customer_id
    if status:
        filter_query["status"] = status

    cursor = db.orders.find(filter_query).skip(skip).limit(limit).sort("created_at", -1)
    orders = await cursor.to_list(length=limit)
    return orders

@app.get("/api/orders/{order_id}", response_model=Order)
async def get_order(order_id: str, db=Depends(get_database)):
    order = await db.orders.find_one({"_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/api/orders/{order_id}/status")
async def update_order_status(order_id: str, status_update: StatusUpdate, db=Depends(get_database)):
    valid_statuses = {
        STATUS_PENDING, STATUS_CONFIRMED, STATUS_PROCESSING,
        STATUS_SHIPPED, STATUS_DELIVERED, STATUS_CANCELLED
    }
    
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid order status")

    current_order = await db.orders.find_one({"_id": order_id})
    if not current_order:
        raise HTTPException(status_code=404, detail="Order not found")

    result = await db.orders.update_one(
        {"_id": order_id},
        {
            "$set": {
                "status": status_update.status,
                "updated_at": datetime.utcnow()
            }
        }
    )

    if result.modified_count:
        order_status_updates.labels(
            current_order["status"],
            status_update.status
        ).inc()
        
        if status_update.status in [STATUS_DELIVERED, STATUS_CANCELLED]:
            active_orders.dec()
            
        return {"status": "success", "message": "Order status updated successfully"}
    
    raise HTTPException(status_code=404, detail="Order not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8087)