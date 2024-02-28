from typing import Optional

from sqlalchemy import create_engine, MetaData, Integer, String, ForeignKey, union_all
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

from sqlalchemy import insert, select, update, text
# from sqlalchemy.orm import Session


# Create engine
engine = create_engine('sqlite+pysqlite:///data/db.sqlite3', echo=True)

# Create Metadata class
class Base(DeclarativeBase):
    pass

# Create ORM Tables
class User(Base):
    __tablename__ = "user_account"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    addresses: Mapped[list["Address"]] = relationship(back_populates="user")
    
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id = mapped_column(ForeignKey("user_account.id"))
    
    user: Mapped[User] = relationship(back_populates="addresses")
    
    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r}, user_id={self.user_id!r})"

# Create DB with metadata
# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
