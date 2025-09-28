"""Sample SQLModel models for testing purposes (v1)."""

from sqlmodel import Field, SQLModel


class Gadget(SQLModel, table=True):
    """Sample SQLModel model for testing (v1)."""

    __tablename__ = "gadgets"
    id: int | None = Field(default=None, primary_key=True)
    name: str
