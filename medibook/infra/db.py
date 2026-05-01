from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from medibook.config.booking_config import BookingConfig



config = BookingConfig()

#Aqui se crea el engine de SQLALchemy usndo la url de la bd
engine = create_engine(config.db_url, echo=True, future=True)

#este es el creador de sesiones para intersactuar con la bd

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

#Clase para los modelos ORM

Base = declarative_base()



