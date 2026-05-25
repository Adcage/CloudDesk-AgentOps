"""通用仓储基类"""

from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """通用仓储基类"""

    def __init__(self, db: Session, model: type[ModelType]):
        self.db = db
        self.model = model

    def get_by_id(self, item_id: int) -> ModelType | None:
        return self.db.get(self.model, item_id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.db.add(instance)
        return instance

    def delete(self, item_id: int) -> bool:
        instance = self.get_by_id(item_id)
        if instance:
            self.db.delete(instance)
            return True
        return False
