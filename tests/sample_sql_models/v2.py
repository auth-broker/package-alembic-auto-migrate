"""Sample SQLModel models for testing purposes (v2)."""

from sqlmodel import Field, SQLModel


class Gadget(SQLModel, table=True):
    """Sample SQLModel model for testing (v2)."""

    __tablename__ = "gadgets"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    # NEW COLUMN compared to v1
    description: str | None = Field(default=None, nullable=True)
