import unittest
import random
from faker import Faker

from src.logica.manager_eporra import ManagerEPorra
from src.modelo.declarative_base import crear_session, TESTING_ADDRESS
from src.modelo.apuesta import Apuesta
from src.modelo.apostador import Apostador
from src.modelo.carrera import Carrera
from src.modelo.competidor import Competidor


class ApuestaTestCase(unittest.TestCase):

    def setUp(self):
        """
        Metodo encargado de la inicializacion de los fixtures de la clase.
        """
        self.data_factory = Faker()
        Faker.seed(0)
        self.logica = ManagerEPorra(TESTING_ADDRESS)
        (self.engine, self.session) = crear_session(TESTING_ADDRESS)

    def tearDown(self):
        """
        Metodo encargado de limpiar los fixtures de la clase.
        """
        self.session.query(Apostador).delete()
        self.session.query(Apuesta).delete()
        self.session.query(Competidor).delete()
        self.session.query(Carrera).delete()

        self.session.commit()
        return super().tearDown()

    def _popular_datos_para_apuesta(self):
        self.apostador_1 = Apostador(nombre=self.data_factory.name())
        self.apostador_2 = Apostador(nombre=self.data_factory.name())
        self.carrera = Carrera(nombre=self.data_factory.name(), abierta=True, ganancia=0)
        self.competidor = Competidor(nombre=self.data_factory.name(), probabilidad=1, carrera=self.carrera)

        self.session.add(self.apostador_1)
        self.session.add(self.apostador_2)
        self.session.add(self.carrera)
        self.session.add(self.competidor)

        self.session.commit()

    def test_aniadir_apuesta(self):
        """
        Metodo encargado de probar la creación de apuestas en e-porra
        """
        self._popular_datos_para_apuesta()
        valor_apuesta = 100

        self.logica.crear_apuesta(
            self.apostador_1.nombre,
            self.carrera.nombre,
            valor_apuesta,
            self.competidor.nombre
        )

        base_apuesta = self.session.query(Apuesta).join(Carrera).filter(
            Carrera.nombre == self.carrera.nombre).first()

        self.assertIsNotNone(base_apuesta, "Se debe crear la apuesta")
        self.assertEqual(base_apuesta.valor, valor_apuesta, "El valor de la apuesta no es el esperado.")

    def test_aniadir_apuesta_valor_menor_o_igual_a_cero(self):
        """
        Metodo encargado de probar la creación de apuestas en e-porra cuando
        se tiene un valor menor al minimo
        """
        self._popular_datos_para_apuesta()

        valor_apuesta = 0
        with self.assertRaises(ValueError):
            self.logica.crear_apuesta(
                self.apostador_1.nombre,
                self.carrera.nombre,
                valor_apuesta,
                self.competidor.nombre
            )

        valor_apuesta = -1
        with self.assertRaises(ValueError):
            self.logica.crear_apuesta(
                self.apostador_1.nombre,
                self.carrera.nombre,
                valor_apuesta,
                self.competidor.nombre
            )
    
    def test_aniadir_apuesta_con_carrera_terminada(self):
        """
        Metodo encargado de probar la creación de apuestas en e-porra cuando
        se tiene una carrera que ya ha terminado
        """
        self._popular_datos_para_apuesta()
        self.carrera.abierta = False
        self.session.commit()

        valor_apuesta = 100
        with self.assertRaises(Exception):
            self.logica.crear_apuesta(
                self.apostador.nombre,
                self.carrera.nombre,
                valor_apuesta,
                self.competidor.nombre
            )
    
    def test_dar_apuestas_carrera(self):
        """
        Metodo encargado de probar la lista de apuestas para una carrera.
        """
        self._popular_datos_para_apuesta()

        self.competidor.probabilidad = 0.5
        
        base_apuestas = []
        base_apuestas.append(Apuesta(valor=10, ganancia=0, carrera=self.carrera,
            apostador=self.apostador_1, competidor=self.competidor
        ))
        base_apuestas.append(Apuesta(valor=10, ganancia=0, carrera=self.carrera,
            apostador=self.apostador_2, competidor=self.competidor
        ))

        self.session.add(base_apuestas[0])
        self.session.add(base_apuestas[1])
        self.session.commit()

        apuestas = self.logica.dar_apuestas_carrera(self.carrera.nombre)

        base_apuestas_nombres = [a.nombre_apostador for a in sorted(base_apuestas, key=lambda ap: ap.nombre_apostador)]
        apuestas_nombre = [a['Apostador'] for a in apuestas]
        
        self.assertEqual(apuestas_nombre, base_apuestas_nombres)

    def test_editar_apuestas_carrera(self):
        """
        Metodo encargado de probar la edición de apuestas para una carrera.
        """
        self._popular_datos_para_apuesta()
        
        valor_1 = random.randint(1, 100)
        valor_2 = random.randint(1, 100)
        valor = random.randint(1, 100)
        base_apuestas = []
        base_apuestas.append(Apuesta(valor=valor_1, ganancia=0, carrera=self.carrera,
            apostador=self.apostador_1, competidor=self.competidor
        ))
        base_apuestas.append(Apuesta(valor=valor_2, ganancia=0, carrera=self.carrera,
            apostador=self.apostador_2, competidor=self.competidor
        ))

        self.session.add(base_apuestas[0])
        self.session.add(base_apuestas[1])
        self.session.commit()

        self.logica.editar_apuesta(0, self.apostador_1.nombre, self.carrera.nombre, valor, self.competidor.nombre)
        apuestas = self.logica.dar_apuestas_carrera(self.carrera.nombre)
        
        base_apuestas_nombres = [a.nombre_apostador for a in sorted(base_apuestas, key=lambda ap: ap.nombre_apostador)]
        apuestas_nombre = [a['Apostador'] for a in apuestas]
        
        self.assertEqual(apuestas_nombre, base_apuestas_nombres)
        
    def test_editar_apuestas_carrera_valor_mayor_uno(self):
        """
        Metodo encargado de probar la edición de apuestas para una carrera.
        """
        self._popular_datos_para_apuesta()
        
        valor_1 = random.randint(1, 100)
        valor_2 = random.randint(1, 100)
        valor = random.randint(-100, 1)
        base_apuestas = []
        base_apuestas.append(Apuesta(valor=valor_1, ganancia=0, carrera=self.carrera,
            apostador=self.apostador_1, competidor=self.competidor
        ))

        self.session.add(base_apuestas[0])
        self.session.commit()

        self.logica.editar_apuesta(0, self.apostador_1.nombre, self.carrera.nombre, valor, self.competidor.nombre)
        apuestas = self.logica.dar_apuestas_carrera(self.carrera.nombre)
        
        self.assertEqual(apuestas[0]['Valor'], valor_1)
        
    def test_editar_apuestas_carrera_valor_no_vacio(self):
        """
        Metodo encargado de probar la edición de apuestas para una carrera.
        """
        self._popular_datos_para_apuesta()
        
        valor_1 = random.randint(1, 100)
        valor_2 = random.randint(1, 100)
        valor = None
        base_apuestas = []
        base_apuestas.append(Apuesta(valor=valor_1, ganancia=0, carrera=self.carrera,
            apostador=self.apostador_1, competidor=self.competidor
        ))

        self.session.add(base_apuestas[0])
        self.session.commit()

        self.logica.editar_apuesta(0, self.apostador_1.nombre, self.carrera.nombre, valor, self.competidor.nombre)
        apuestas = self.logica.dar_apuestas_carrera(self.carrera.nombre)
        
        self.assertEqual(apuestas[0]['Valor'], valor_1)