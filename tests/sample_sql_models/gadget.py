"""Sample SQLModel model for testing."""

from sqlmodel import Field, SQLModel


class Gadget(SQLModel, table=True):
    """Sample SQLModel model for testing."""

    __tablename__ = "gadgets"
    id: int | None = Field(default=None, primary_key=True)
    name: str
