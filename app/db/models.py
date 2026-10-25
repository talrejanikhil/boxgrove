from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class OrderStatus(StrEnum):
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    RETURNED = "returned"


class ItemStatus(StrEnum):
    ACTIVE = "active"
    RETURN_REQUESTED = "return_requested"
    RETURNED = "returned"


class ReturnStatus(StrEnum):
    REQUESTED = "requested"
    APPROVED = "approved"
    REFUNDED = "refunded"


def utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    products: Mapped[list[Product]] = relationship(back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[float]
    currency: Mapped[str] = mapped_column(default="USD")
    stock_qty: Mapped[int] = mapped_column(default=0)
    sku: Mapped[str] = mapped_column(unique=True)

    category: Mapped[Category] = relationship(back_populates="products")


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)

    orders: Mapped[list[Order]] = relationship(back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.PROCESSING)
    total: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    customer: Mapped[Customer] = relationship(back_populates="orders")
    items: Mapped[list[OrderItem]] = relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    qty: Mapped[int]
    unit_price: Mapped[float]
    status: Mapped[ItemStatus] = mapped_column(default=ItemStatus.ACTIVE)

    order: Mapped[Order] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()
    returns: Mapped[list[Return]] = relationship(back_populates="order_item")


class Return(Base):
    __tablename__ = "returns"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_item_id: Mapped[int] = mapped_column(ForeignKey("order_items.id"))
    status: Mapped[ReturnStatus] = mapped_column(default=ReturnStatus.REQUESTED)
    reason: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    order_item: Mapped[OrderItem] = relationship(back_populates="returns")
