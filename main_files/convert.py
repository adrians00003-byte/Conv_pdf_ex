from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional, List

class InvoiceItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    rate: Optional[float] = None
    amount: Optional[float] = None
    category: Optional[str] = None

class Invoice(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_file: str
    template: str = Field(default="temaplate")

    invoice_number: str
    seller_name: str
    bill_to: Optional[str] = None
    ship_to: Optional[str] = None

    issue_data: Optional[date] = None
    ship_mode: Optional[str] = None
    order_id: Optional[str] = None

    subtotal: Optional[float] = None
    discount_amount: Optional[float] = None
    shipping: Optional[float] = None
    total: Optional[float] = None

    items: List[InvoiceItem] = Field(default_factory=list)