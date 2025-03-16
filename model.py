from sqlalchemy import (
    String
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from base import Base, create_db
import bcrypt



class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(240), nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    def __init__(self, email, name, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password.encode())


class Product(Base):
    __tablename__ = "product"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(240), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    image: Mapped[str] = mapped_column(String(240), nullable=True)

    def __str__(self):
        return self.name.capitalize()

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
