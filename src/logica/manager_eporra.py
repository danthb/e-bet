from src.modelo.declarative_base import Base, crear_session
from src.modelo.apuesta import Apuesta
from src.modelo.apostador import Apostador
from src.modelo.competidor import Competidor
from src.modelo.carrera import Carrera
from .Logica_mock import Logica_mock


class ManagerEPorra(Logica_mock):
    """
    Clase principal para el manejo de la logica de la pagina E-Porra
    """

    def __init__(self, address) -> None:
        """
        Metodo contructor de la clase para la logica. En esta se inicializa
        el motor para la conexion con la BD.
        """
        (self.engine, self.session) = crear_session(address)
        Base.metadata.create_all(self.engine)
        super(ManagerEPorra, self).__init__()

    def guardar_cambios_carrera(self, nombre, competidores, nueva_carrera):
        """Metodo encargado de gestionar la logica para crear una carrera"""
        try:
            carrera = self._crear_carrera(
                nombre) if nueva_carrera else self.editar_carrera()

            if sum([c.get('Probabilidad') for c in competidores]) != 1:
                raise Exception(
                    "Las probabilidades de los competidores no son iguales a 1")

            for i, competidor in enumerate(competidores):
                if competidor.get('Estado') == 'Nueva':
                    self.aniadir_competidor(
                        carrera, competidor['Nombre'], competidor['Probabilidad'])
                else:
                    self.editar_competidor(
                        i, competidor['Nombre'], competidor['Probabilidad'])
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def _crear_carrera(self, nombre):
        """
        Metodo para aniadir un competidor a la carrera.

        Args:
            nombre: nombre de la carrera.
        """
        nombre = nombre.strip()
        if len(nombre) == 0:
            raise Exception("El nombre de la carrera no debe estar vacio")
        elif len(nombre) > 200:
            raise ValueError(
                "El nombre de la carrera puede tener hasta 200 caracteres")
        elif self.dar_carrera(nombre) is not None:
            raise ValueError(
                "Ya existe una carrera con nombre: {}".format(nombre))

        carrera = Carrera(nombre=nombre, abierta=True, ganancia=None)
        self.session.add(carrera)

        return carrera

    def aniadir_apostador(self, nombre):
        """Metodo para crear apostadores en E-Porra (Semana 7)"""
        if nombre is None or len(nombre) <= 0 or len(nombre) > 200:
            raise ValueError(
                "El nombre del apostador debe tener entre 1 y 200 caracteres")
        elif self.dar_apostador(nombre) is not None:
            raise ValueError("Ya existe un apostador con el mismo nombre")
        self.session.add(Apostador(nombre=nombre))
        self.session.commit()

    def aniadir_competidor(self, carrera, nombre, probabilidad):
        """
        Metodo para aniadir un competidor a la carrera.
        """
        if len(nombre.strip()) == 0:
            raise Exception("El nombre del competidor no puede estar vacio")
        elif self.session.query(Competidor).filter(Competidor.nombre == nombre).first() is not None:
            raise ValueError(
                "Ya existe un competidor con el nombre: " + nombre)
        elif len(nombre) > 200:
            raise ValueError(
                "El nombre del competidor no puede tener mas de 200 caracteres")
        elif not isinstance(probabilidad, (int, float)):
            raise ValueError("La probabilidad debe ser un número")
        elif probabilidad <= 0 or probabilidad >= 1:
            raise ValueError("La probabilidad debe ser mayor a 0 y menor a 1")

        competidor = Competidor(
            nombre=nombre, probabilidad=probabilidad, ganador=False)
        carrera.competidores.append(competidor)

    def crear_apuesta(self, nombre_apostador, id_carrera, valor, nombre_competidor):
        """
        Metodo para la creacion de una apuesta en e-porra

        Args:
            nombre_apostador (str): Nombre del apostador que realiza la apuesta
            id_carrera (str): Identificador de la carrera a la que se le hace la apuesta
            valor (number): Valor de la apuesta a realizar
            nombre_competidor (str): nombre del competidor a quien se le hace la apuesta
        """
        if valor <= 0:
            raise ValueError(
                'El valor de la apuesta debe serpositivo y mayor a cero')

        carrera = self.dar_carrera(id_carrera)

        if not carrera.abierta:
            raise Exception(
                "La carrera ya ha finalizado, no es posible adicionar apuestas.")

        apostador = self.dar_apostador(nombre_apostador)
        competidor = self.dar_competidor(id_carrera, nombre_competidor)

        apuesta = Apuesta(valor=valor, ganancia=0, carrera=carrera,
                          apostador=apostador, competidor=competidor)

        self.session.add(apuesta)
        self.session.commit()

    def dar_carreras(self):
        """
        Metodo para obtener las carreras de la base de datos.
        """
        carreras = [cr.map_interfaz() for cr in self.session.query(
            Carrera).order_by(Carrera.nombre.asc()).all()]
        return carreras

    def dar_apostadores(self):
        """Metodo para obtener la lista de apostadores en e-porra (semana 7)"""
        apostadores = self.session.query(Apostador).order_by(
            Apostador.nombre.asc()).all()
        return [apostador.map_interfaz() for apostador in apostadores]

    def dar_carrera(self, nombre):
        """Metodo para obtener una carrera a partir de su nombre"""
        return self.session.query(Carrera).filter(Carrera.nombre == nombre).first()

    def dar_apostador(self, nombre):
        """Metodo para obtener una carrera a partir de su nombre"""
        return self.session.query(Apostador).filter(Apostador.nombre == nombre).first()

    def dar_competidor(self, id_carrera, id_competidor):
        """Metodo para obtener una carrera a partir de su nombre"""
        return self.session.query(Competidor).join(Carrera).filter(
            Competidor.nombre == id_competidor,
            Carrera.nombre == id_carrera).first()

    def dar_competidores_carrera(self, nombre):
        """Metodo para obtener los competidores de una carrera especifica"""
        carrera = self.dar_carrera(nombre)
        return [competidor.map_interfaz() for competidor in carrera.competidores]

    def terminar_carrera(self, nombre_ganador):
        """
        Metodo para elegir el ganador de una carrera.
        """
        if(nombre_ganador is None or len(nombre_ganador) == 0):
            raise Exception("Debe seleccionar un ganador")
        else:
            competidor = self.session.query(Competidor).filter(
                Competidor.nombre == nombre_ganador).first()
            competidor.ganador = True
            carrera = competidor.carrera
            self.session.query(Carrera).filter(
                Carrera.nombre == carrera.nombre).update({Carrera.abierta: False})
            self.session.commit()

    def dar_apuestas_carrera(self, nombre, uso_interno=False):
        """Metodo para obtener las apuestas de una carrera especifica"""
        apuestas = self.session.query(Apuesta).join(
            Carrera).filter(Carrera.nombre == nombre)
        apuestas = apuestas.order_by(Apuesta.nombre_apostador).all()
        return [apuesta.map_interfaz() for apuesta in apuestas] \
            if not uso_interno else apuestas

    def dar_reporte_ganancias(self, id_carrera, id_competidor):
        """Metodo para generar el reporte de ganancias de una carrera"""
        carrera = self.dar_carrera(id_carrera)
        competidor = self.dar_competidor(id_carrera, id_competidor)

        apuestas = self.dar_apuestas_carrera(id_carrera, uso_interno=True)
        ganancias = [self._ganancia_apuesta(a, competidor) for a in apuestas]

        carrera.ganancia = sum(a.valor for a in apuestas) - \
            sum(j for i, j in ganancias)

        self.session.commit()
        return sorted(ganancias, key=lambda g: g[0]), carrera.ganancia

    def _ganancia_apuesta(self, apuesta, ganador):
        """
        Metodo para calcular la ganancia de una apuesta a partir de su informacion
        y el ganador de la carrera.

        Args:
            apuesta (obj: Apuesta): Apuesta para calcular la ganancia. 
            ganador (obj: Competidor): Ganador de la carrera 
        """
        ganancia = 0
        if apuesta.nombre_competidor == ganador.nombre:
            ganancia = apuesta.valor / \
                (ganador.probabilidad/(1-ganador.probabilidad))
            ganancia = round(ganancia + apuesta.valor, 2)

        apuesta.ganancia = ganancia
        return (apuesta.nombre_apostador, ganancia)

    def eliminar_carrera(self, nombre_carrera):
        """
        Metodo para eliminar una carrera.
        """
        resultado = 0
        apuestas_carrera = self.dar_apuestas_carrera(nombre_carrera)
        if apuestas_carrera:
            return resultado
        else:
            self.session.query(Carrera).filter(Carrera.nombre == nombre_carrera).delete()
            self.session.commit()
            resultado = 1
            return resultado

    def editar_apuesta(self, id_apuesta, apostador, carrera, valor, competidor):
        """
        Metodo para editar una apuesta.
        
        """
        try:
            if valor is not None and valor > 1:
                apuesta_seleccionada = self.dar_apuestas_carrera(carrera)[id_apuesta]
                apostador_anterior, competidor_anterior = apuesta_seleccionada['Apostador'],  apuesta_seleccionada['Competidor']
                self.session.query(Apuesta).\
                    filter_by(nombre_apostador = apostador_anterior, nombre_competidor=competidor_anterior).update({
                        Apuesta.valor: valor,
                        Apuesta.nombre_apostador: apostador,
                        Apuesta.nombre_competidor: competidor
                })
                self.session.commit()
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False