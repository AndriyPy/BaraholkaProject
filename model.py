from sqlalchemy import String, ForeignKey, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
from base import Base, create_db
import bcrypt


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(240), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    products: Mapped[list["Product"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __init__(self, email, name, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password.encode())

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"



class Product(Base):
    __tablename__ = "products"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(240), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    image = mapped_column(LargeBinary, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="products")

    def __str__(self):
        return self.name.capitalize()

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
