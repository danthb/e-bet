from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .declarative_base import Base

class Apostador(Base):
    __tablename__ = 'apostador'

    nombre = Column(String, primary_key=True)

    apuestas = relationship('Apuesta', backref='apostador',
                                cascade='all, delete, delete-orphan')

    def map_interfaz(self):
        """
        Metodo para hacer el mapping entre el ORM y 
        los dict utilizados por la interfaz
        """
        return {
            'Nombre': self.nombre,
        }
