from __future__ import annotations
from sqlmodel import SQLModel, Field

class Gadget(SQLModel, table=True):
    __tablename__ = "gadgets"
    id: int | None = Field(default=None, primary_key=True)
    name: str
