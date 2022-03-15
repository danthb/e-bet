import unittest
from faker import Faker

from src.logica.manager_eporra import ManagerEPorra
from src.modelo.declarative_base import crear_session, TESTING_ADDRESS
from src.modelo.apuesta import Apuesta
from src.modelo.apostador import Apostador
from src.modelo.carrera import Carrera
from src.modelo.competidor import Competidor


class CompetidorTestCase(unittest.TestCase):
	"""
	Clase para la creacion the pruebas unitarias, especificamente para la logica
	relacionada a los competidores de E-Porra
	"""

	def setUp(self):
		"""
		Metodo encargado de la inicializacion de los fixtures de la clase.
		"""
		self.data_factory = Faker()
		Faker.seed(0)
		self.logica = ManagerEPorra(TESTING_ADDRESS)
		(self.engine, self.session)= crear_session(TESTING_ADDRESS)

		self.carrera = Carrera(nombre=self.data_factory.name(), abierta=True, ganancia=None)
		self.session.add(self.carrera)
		self.session.commit()

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

	def test_aniadir_competidor(self):
		"""
		Metodo encargado de probar la creacion de un competidor en e-porra.
		"""
		nombre= self.data_factory.name()
		probabilidad = 0.5
		ganador = False

		self.logica.aniadir_competidor(self.carrera, nombre, probabilidad)

		base_competidor = self.session.query(Competidor).filter(Competidor.nombre == nombre).first()
		self.assertIsNotNone(base_competidor, "El competidor no fue creado en la base de datos de prueba")
		self.assertEqual(base_competidor.nombre, nombre, "El competidor no tiene el nombre esperado")
		self.assertEqual(base_competidor.probabilidad, probabilidad, "El competidor no tiene la probabilidad esperada")
		self.assertEqual(base_competidor.ganador, ganador, "El competidor no tiene la probabilidad esperada")

	def test_aniadir_competidor_sin_nombre(self):
		"""
		Metodo encargado de probar la creacion de un competidor en e-porra, 
		cuando no se coloca un nombre. Se espera que un competidor sin nombre no sea
		guardado.
		"""

		nombre = ""
		probabilidad = 0.5

		with self.assertRaises(Exception):
			self.logica.aniadir_competidor(self.carrera, nombre, probabilidad)

	def test_aniadir_competidor_duplicado(self):
		"""
		Metodo encargado de probar la creacion de un competidor en e-porra,
		cuando ya existe un competidor con el mismo nombre. Se espera que un competidor
		con nombre duplicado no sea guardado.
		"""
		nombre= self.data_factory.name()
		probabilidad = 0.5

		competidor = Competidor(nombre=nombre, probabilidad=probabilidad, carrera=self.carrera)
		self.session.add(competidor)
		self.session.commit()

		with self.assertRaises(ValueError):
			self.logica.aniadir_competidor(self.carrera, nombre, probabilidad)
		
		num_competidores = self.session.query(Competidor).filter(Competidor.nombre == nombre).count()
		self.assertEqual(num_competidores, 1, "No se deben crear competidores con nombres duplicados")

	def test_aniadir_competidor_probabilidad_menor_o_igual_a_cero(self):
		"""
		Metodo encargado de probar la creacion de un competidor en e-porra,
		cuando se tiene una probabilidad menor o igual a cero. Se espera que el competidor
		no sea guardado
		"""
		nombre= self.data_factory.name()
		probabilidad = -0.5

		with self.assertRaises(ValueError):
			self.logica.aniadir_competidor(self.carrera, nombre, probabilidad)
		
		probabilidad = 0
		with self.assertRaises(ValueError):
			self.logica.aniadir_competidor(self.carrera, nombre, probabilidad)
		
	def test_aniadir_competidor_probabilidad_mayor_o_igual_a_uno(self):
		"""
		Metodo encargado de probar la creacion de un competidor en e-porra,
		cuando se tiene una probabilidad mayor a 1. Se espera que el competidor
		no sea guardado
		"""
		nombre= self.data_factory.name()
		
		probabilidad = 1
		with self.assertRaises(ValueError):
			self.logica.aniadir_competidor(self.carrera, nombre, probabilidad)

		probabilidad = 1.1
		with self.assertRaises(ValueError):
			self.logica.aniadir_competidor(self.carrera, nombre, probabilidad)
		

	def test_aniadir_competidor_con_probabilidad_no_numerica(self):
		"""
		Metodo encargado de probar la creacion de un competidor en e-porra,
		cuando el valor de la probabilidad no es numerico. Se espera que el competidor
		no sea guardado.
		"""

		nombre= self.data_factory.name()
		probabilidad = None

		with self.assertRaises(ValueError):
			self.logica.aniadir_competidor(self.carrera, nombre, probabilidad)

		probabilidad = "0.5"
		with self.assertRaises(ValueError):
			self.logica.aniadir_competidor(self.carrera, nombre, probabilidad)
		
		probabilidad = "cero"
		with self.assertRaises(ValueError):
			self.logica.aniadir_competidor(self.carrera, nombre, probabilidad)


	def test_aniadir_competidor_tamano_nombre_superior_a_200_caracteres(self):
		"""
		Metodo encargado de probar la creacion de un competidor en e-porra,
		cuando el nombre tiene mas de 200 caracteres. Se espera que el competidor
		no sea guardado
		"""
		nombre= "a" * 201
		probabilidad = 0.5

		with self.assertRaises(ValueError):
			self.logica.aniadir_competidor(self.carrera, nombre, probabilidad)