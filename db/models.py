from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
# Модели
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    evm_private: Mapped[str] = mapped_column(unique=True)
    evm_address: Mapped[str] = mapped_column(unique=True)
    sol_private: Mapped[str] = mapped_column(nullable=True)
    sol_address: Mapped[str] = mapped_column(nullable=True)
    proxy: Mapped[str] = mapped_column(nullable=True)
    common_chests: Mapped[int] = mapped_column(default=0)
    epic_chests: Mapped[int] = mapped_column(default=0)
    legendary_chests: Mapped[int] = mapped_column(default=0)

