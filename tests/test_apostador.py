import unittest
from faker import Faker

from src.logica.manager_eporra import ManagerEPorra
from src.modelo.declarative_base import crear_session, TESTING_ADDRESS
from src.modelo.apuesta import Apuesta
from src.modelo.apostador import Apostador
from src.modelo.carrera import Carrera
from src.modelo.competidor import Competidor


class ApostadorTestCase(unittest.TestCase):

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
    
    def test_aniadir_apostador(self):
        """
        Metodo encargado de probar la creación de apostadores en e-porra
        """
        nombre = self.data_factory.name()
        self.logica.aniadir_apostador(nombre)

        base_apostador = self.session.query(Apostador).filter(
            Apostador.nombre == nombre
        ).first()

        self.assertIsNotNone(base_apostador)
        self.assertEqual(base_apostador.nombre, nombre)
    
    def test_aniadir_apostador_nombre_vacio(self):
        """
        Metodo encargado de probar la creacion de un apostador en e-porra,
        cuando no se coloca un nombre. Se espera que un apostador sin nombre no sea
        guardado.
        """
        nombre = ''
        with self.assertRaises(ValueError):
            self.logica.aniadir_apostador(nombre)
        
        nombre = None
        with self.assertRaises(ValueError):
            self.logica.aniadir_apostador(nombre)
    
    def test_aniadir_apostador_nombre_tamano_invalido(self):
        """
        Metodo encargado de probar la creacion de un apostador en e-porra,
        cuando el nombre tiene mas de 200 characteres. Se espera que el apostador
        no sea guardado.
        """
        nombre = self.data_factory.pystr(min_chars=201, max_chars=300)

        with self.assertRaises(ValueError):
            self.logica.aniadir_apostador(nombre)
    
    def test_aniadir_apostador_con_nombre_duplicado(self):
        """
        Metodo encargado de probar la creacion de un apostador en e-porra,
        cuando ya esxiste un apostador con el mismo nombre. Se espera que el apostador
        no sea guardado.
        """
        nombre = self.data_factory.name()
        self.session.add(Apostador(nombre=nombre))
        self.session.commit()

        with self.assertRaises(ValueError):
            self.logica.aniadir_apostador(nombre)

    def test_dar_apostadores_orden_lista(self):
        """
        Método encargado para verificar que la lista de apostadores se encuentre
        ordenada por el nombre de los apostadores.
        """
        base_apostadores = []
        for ap in range(4):
            base_apostadores.append(Apostador(nombre=self.data_factory.name()))
            self.session.add(base_apostadores[ap])
        self.session.commit()

        base_apostadores = sorted(base_apostadores, key=lambda ap: ap.nombre)
        apostadores = self.logica.dar_apostadores()

        self.assertEqual([g['Nombre'] for g in apostadores], [ap.nombre for ap in base_apostadores])


        