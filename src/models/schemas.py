"""Schema definitions for e-commerce data."""
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
from enum import Enum


class ProductCategory(Enum):
    LUMBER = "Lumber & Building Materials"
    ELECTRICAL = "Electrical"
    PLUMBING = "Plumbing"
    PAINT = "Paint"
    HARDWARE = "Hardware"
    TOOLS = "Tools"
    APPLIANCES = "Appliances"
    FLOORING = "Flooring"
    GARDEN = "Lawn & Garden"
    KITCHEN = "Kitchen & Bath"


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


@dataclass
class Product:
    product_id: str
    sku: str
    product_name: str
    category: ProductCategory
    subcategory: str
    brand: str
    unit_price: float
    unit_cost: float
    weight_lbs: float
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class Store:
    store_id: str
    store_name: str
    store_type: str
    city: str
    state: str
    region: str
    is_active: bool


@dataclass
class Customer:
    customer_id: str
    customer_type: str
    email: str
    first_name: str
    last_name: str
    state: str
    loyalty_tier: str
    created_at: datetime


@dataclass
class Transaction:
    transaction_id: str
    order_id: str
    customer_id: str
    store_id: str
    product_id: str
    transaction_date: datetime
    quantity: int
    unit_price: float
    discount_amount: float
    total_amount: float
    order_status: OrderStatus
    channel: str
    fulfillment_type: str