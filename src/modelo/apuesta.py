from sqlalchemy import Column, ForeignKey, Integer, Numeric, String

from .declarative_base import Base

class Apuesta(Base):
    __tablename__ = 'apuesta'

    id = Column(Integer, primary_key=True)
    valor = Column(Numeric)
    ganancia = Column(Numeric)

    nombre_apostador = Column(String, ForeignKey('apostador.nombre'))
    nombre_competidor = Column(String, ForeignKey('competidor.nombre'))
    nombre_carrera = Column(String, ForeignKey('carrera.nombre'))


    def map_interfaz(self):
        return {
            'Valor': self.valor,
            'Ganancia': self.ganancia,
            'Competidor': self.nombre_competidor,
            'Apostador': self.nombre_apostador,
        }