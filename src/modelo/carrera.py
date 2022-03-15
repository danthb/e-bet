from sqlalchemy import Boolean, Column, Numeric, String
from sqlalchemy.orm import relationship

from .declarative_base import Base

class Carrera(Base):
    __tablename__ = 'carrera'

    nombre = Column(String, primary_key=True)
    abierta = Column(Boolean)
    ganancia = Column(Numeric)

    competidores = relationship('Competidor', backref='carrera',
                                cascade='all, delete, delete-orphan')
    apuestas = relationship('Apuesta', backref='carrera',
                            cascade='all, delete, delete-orphan')

    def map_interfaz(self):
        return {
            'Nombre': self.nombre,
            'Abierta': self.abierta,
            'Ganancia': self.ganancia,
            'Competidores': [c.map_interfaz() for c in self.competidores]
        }