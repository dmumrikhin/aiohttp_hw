import os
import datetime
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker 
from sqlalchemy.ext.asyncio import AsyncAttrs 
from sqlalchemy.orm import DeclarativeBase 
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func

POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'secret')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'app')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'app')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5431')

PG_DSN = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase): 
    pass

class Adverts(Base):
    __tablename__ = 'adverts'

    id: Mapped[int] = mapped_column(primary_key=True)
    header: Mapped[str] = mapped_column(String(70), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False) 
    creation_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    owner: Mapped[str] = mapped_column(String(50), nullable=False)

    @property                            
    def dict(self):
        return {
            'id': self.id,
            'header': self.header,
            'description': self.description,
            'creation_time': self.creation_time.isoformat(),
            'owner': self.owner,
        }


    