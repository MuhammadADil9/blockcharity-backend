from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from config.database import Base


# Generic type for SQLAlchemy model
ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """
    Base repository with CRUD operations.
    All specific repositories inherit from this.
    """
    
    def __init__(self, model: Type[ModelType], db_session: Session):
        self.model = model
        self.db = db_session
    
    def get(self, id: Any) -> Optional[ModelType]:
        """Get by primary key (assumes 'id' column exists)"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_by(self, **kwargs) -> Optional[ModelType]:
        """Get first record matching filters"""
        query = self.db.query(self.model)
        for key, value in kwargs.items():
            query = query.filter(getattr(self.model, key) == value)
        return query.first()
    
    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = None,
        descending: bool = False
    ) -> List[ModelType]:
        """Get paginated list"""
        query = self.db.query(self.model)
        
        if order_by:
            order_column = getattr(self.model, order_by)
            if descending:
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))
        
        return query.offset(skip).limit(limit).all()
    
    def get_multi_by(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[ModelType]:
        """Get multiple records matching filters"""
        query = self.db.query(self.model)
        for key, value in filters.items():
            query = query.filter(getattr(self.model, key) == value)
        return query.offset(skip).limit(limit).all()
    
    def count(self, **filters) -> int:
        """Count records matching filters"""
        query = self.db.query(self.model)
        for key, value in filters.items():
            query = query.filter(getattr(self.model, key) == value)
        return query.count()
    
    def create(self, **kwargs) -> ModelType:
        """Create a new record"""
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def create_many(self, items: List[Dict[str, Any]]) -> List[ModelType]:
        """Bulk create records"""
        instances = [self.model(**item) for item in items]
        self.db.add_all(instances)
        self.db.commit()
        for instance in instances:
            self.db.refresh(instance)
        return instances
    
    def update(self, id: Any, **kwargs) -> Optional[ModelType]:
        """Update a record by primary key"""
        instance = self.get(id)
        if not instance:
            return None
        
        for key, value in kwargs.items():
            if hasattr(instance, key) and value is not None:
                setattr(instance, key, value)
        
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def update_by(self, filters: Dict[str, Any], **kwargs) -> int:
        """Update multiple records matching filters. Returns count updated."""
        query = self.db.query(self.model)
        for key, value in filters.items():
            query = query.filter(getattr(self.model, key) == value)
        
        count = query.update(kwargs, synchronize_session=False)
        self.db.commit()
        return count
    
    def delete(self, id: Any) -> bool:
        """Delete by primary key"""
        instance = self.get(id)
        if not instance:
            return False
        self.db.delete(instance)
        self.db.commit()
        return True
    
    def delete_by(self, **filters) -> int:
        """Delete multiple records matching filters. Returns count deleted."""
        query = self.db.query(self.model)
        for key, value in filters.items():
            query = query.filter(getattr(self.model, key) == value)
        
        count = query.delete(synchronize_session=False)
        self.db.commit()
        return count
    
    def exists(self, **filters) -> bool:
        """Check if any record exists matching filters"""
        return self.count(**filters) > 0
    
    def upsert(self, unique_fields: Dict[str, Any], **kwargs) -> ModelType:
        """
        Update if exists, otherwise create.
        unique_fields: dict of fields that determine uniqueness (e.g., {'tx_hash': '0x...'})
        """
        instance = self.get_by(**unique_fields)
        if instance:
            # Update existing
            for key, value in kwargs.items():
                if hasattr(instance, key) and value is not None:
                    setattr(instance, key, value)
            self.db.commit()
            self.db.refresh(instance)
            return instance
        else:
            # Create new
            return self.create(**unique_fields, **kwargs)