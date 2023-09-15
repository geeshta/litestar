import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    # ... other fields follow, but we only require id for this example
