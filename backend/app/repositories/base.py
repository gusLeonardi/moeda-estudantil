from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: type[T]):
        self.db = db
        self.model = model

    def get(self, entity_id: int) -> T | None:
        return self.db.get(self.model, entity_id)

    def list(self) -> list[T]:
        return list(self.db.scalars(select(self.model)).all())

