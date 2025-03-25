from sqlalchemy import Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from datetime import datetime
from typing import List

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100))
    chat_id: Mapped[str] = mapped_column(String(100))
    balance: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    owned_lots: Mapped[List["Lot"]] = relationship(back_populates="owner", foreign_keys="Lot.owner_id")
    bought_lots: Mapped[List["Lot"]] = relationship(back_populates="buyer", foreign_keys="Lot.buyer_id")

class Lot(Base):
    __tablename__ = "lots"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(1000))
    cur_price: Mapped[int] = mapped_column(Integer)
    max_price: Mapped[int] = mapped_column(Integer)
    step: Mapped[int] = mapped_column(Integer)
    time_start: Mapped[datetime] = mapped_column(DateTime)
    time_end: Mapped[datetime] = mapped_column(DateTime)
    
    # Relationships
    owner: Mapped["User"] = relationship(back_populates="owned_lots", foreign_keys=[owner_id])
    buyer: Mapped["User"] = relationship(back_populates="bought_lots", foreign_keys=[buyer_id])
    categories: Mapped[List["Category"]] = relationship(secondary="categories", back_populates="lots")
    pictures: Mapped[List["Pictures"]] = relationship(back_populates="lot")

class Category(Base):
    __tablename__ = "category"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    
    # Relationships
    lots: Mapped[List["Lot"]] = relationship(secondary="categories", back_populates="categories")

class Categories(Base):
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lots_id: Mapped[int] = mapped_column(ForeignKey("lots.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))

class Pictures(Base):
    __tablename__ = "pictures"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(String(255))
    lots_id: Mapped[int] = mapped_column(ForeignKey("lots.id"))
    
    # Relationships
    lot: Mapped["Lot"] = relationship(back_populates="pictures")

# Create database connection
def init_db():
    engine = create_engine("sqlite:///auction.db")
    Base.metadata.create_all(bind=engine)
    
if __name__ == "__main__":
    init_db()