from sqlalchemy import Boolean, Column, Numeric, ForeignKey, String
from sqlalchemy.orm import relationship

from .declarative_base import Base

class Competidor(Base):
    __tablename__ = 'competidor'

    nombre = Column(String, primary_key=True)
    probabilidad = Column(Numeric)
    ganador = Column(Boolean)

    nombre_carrera = Column(String, ForeignKey('carrera.nombre'), primary_key=True)

    apuestas = relationship('Apuesta', backref='competidor',
                                cascade='all, delete, delete-orphan')

    def map_interfaz(self):
        """
        Metodo para hacer el mapping entre el ORM y 
        los dict utilizados por la interfaz
        """
        return {
            'Nombre': self.nombre,
            'Probabilidad': self.probabilidad,
        }
