import unittest
import random
from faker import Faker

from src.logica.manager_eporra import ManagerEPorra
from src.modelo.declarative_base import crear_session, TESTING_ADDRESS
from src.modelo.apuesta import Apuesta
from src.modelo.apostador import Apostador
from src.modelo.carrera import Carrera
from src.modelo.competidor import Competidor


class CarreraTestCase(unittest.TestCase):
    """
    Clase para la creacion the pruebas unitarias, especificamente para la logica
    relacionada a las carreras de E-Porra
    """

    def setUp(self):
        """
        Metodo encargado de la inicializacion de los fixtures de la clase.
        """
        self.data_factory = Faker()
        Faker.seed(0)
        self.logica = ManagerEPorra(TESTING_ADDRESS)
        (self.engine, self.session) = crear_session(TESTING_ADDRESS)

        self.nombre_carrera = self.data_factory.name()
        self.carrera = Carrera(nombre=self.nombre_carrera,
                               abierta=True, ganancia=0)
        self.session.add(self.carrera)

        self.nombre_competidor1 = self.data_factory.name()
        self.nombre_competidor2 = self.data_factory.name()

        self.probabilidad_competidor1 = random.uniform(0, 1)
        self.probabilidad_competidor2 = 1 - self.probabilidad_competidor1

        self.competidor1 = Competidor(
            nombre=self.nombre_competidor1, probabilidad=self.probabilidad_competidor1, ganador=False, carrera=self.carrera)
        self.competidor2 = Competidor(
            nombre=self.nombre_competidor2, probabilidad=self.probabilidad_competidor2, ganador=False, carrera=self.carrera)
        self.session.add(self.competidor1)
        self.session.add(self.competidor2)

        self.session.commit()

    def _popular_datos_reporte(self):
        """
        Metodo encargado de la inicializacion de los fixtures de la clase.
        """
        self.apostador_1 = Apostador(nombre=self.data_factory.name())
        self.apostador_2 = Apostador(nombre=self.data_factory.name())
        self.session.add(self.apostador_1)
        self.session.add(self.apostador_2)
        self.valor_apuesta1 = random.randint(1, 100)
        self.valor_apuesta2 = random.randint(1, 100)
        self.apuesta1 = Apuesta(valor=self.valor_apuesta1, ganancia=0, carrera=self.carrera,
            apostador=self.apostador_1, competidor=self.competidor1
        )
        self.apuesta2 =Apuesta(valor=self.valor_apuesta2, ganancia=0, carrera=self.carrera,
            apostador=self.apostador_2, competidor=self.competidor2
        )
        self.session.add(self.apuesta1)
        self.session.add(self.apuesta2)
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

    def test_dar_carreras(self):
        """
        Metodo encargado de probar la generacion de la lista de carreras en e-porra.
        """
        self.session.query(Carrera).delete()
        self.session.query(Competidor).delete()
        self.session.commit()
        self.assertEqual(len(self.logica.dar_carreras()), 0,
                         "No deberian haber carreras en E-Porra")

        for i in range(10):
            self.session.add(Carrera(nombre="carrera{}".format(
                i), abierta=i % 2 == 0, ganancia=i))
            self.session.commit()

            self.assertEqual(len(self.logica.dar_carreras()), i+1,
                             "El numero de carreras no es el esperado")

    def test_crear_carrera(self):
        """
        Metodo encargado de probar la creacion de una carrera en e-porra.
        """
        nombre = self.data_factory.name()

        self.nombre_competidor1 = self.data_factory.name()
        self.nombre_competidor2 = self.data_factory.name()

        self.probabilidad_competidor1 = random.uniform(0, 1)
        self.probabilidad_competidor2 = 1 - self.probabilidad_competidor1

        competidores = [
            {"Nombre": self.nombre_competidor1, "Probabilidad": self.probabilidad_competidor1, "Estado": "Nueva"},
            {"Nombre": self.nombre_competidor2, "Probabilidad": self.probabilidad_competidor2, "Estado": "Nueva"},
        ]

        self.logica.guardar_cambios_carrera(nombre, competidores, True)

        base_carrera = self.session.query(Carrera).filter(
            Carrera.nombre == nombre).first()
        self.assertIsNotNone(
            base_carrera, "La carrera no fue creada en la base de datos de prueba")
        self.assertEqual(base_carrera.nombre, nombre,
                         "La carrera no tiene el nombre esperado")

    def test_crear_carrera_sin_nombre(self):
        """
        Metodo encargado de probar la creacion de una carrera en e-porra,
        cuando no se coloca un nombre. Se espera que una carrera sin nombre no sea
        guardado.
        """
        nombre = ""

        with self.assertRaises(Exception):
            self.logica.guardar_cambios_carrera(nombre, [], True)

    def test_crear_carrera_duplicada(self):
        """
        Metodo encargado de probar la creacion de una competencia en e-porra,
        cuando ya existe una carrera con el mismo nombre. Se espera que una carrera
        con nombre duplicado no sea guardada.
        """
        nombre = self.data_factory.name()

        carrera = Carrera(nombre=nombre, abierta=True, ganancia=0)
        self.session.add(carrera)
        self.session.commit()

        with self.assertRaises(ValueError) as valueError:
            self.logica.guardar_cambios_carrera(nombre, [], True)

        num_carrera = self.session.query(Carrera).filter(
            Carrera.nombre == nombre).count()
        self.assertEqual(
            num_carrera, 1, "No se deben crear carreras con nombres duplicados")

    def test_crear_carrera_tamano_nombre_superior_a_200_caracteres(self):
        """
        Metodo encargado de probar la creacion de una carrera en e-porra,
        cuando el nombre tiene mas de 200 caracteres, se espera que la carrera
        no sea guardada
        """
        nombre = self.data_factory.name() * 201

        with self.assertRaises(ValueError):
            self.logica.guardar_cambios_carrera(nombre, [], True)

    def test_crear_carrera_suma_probabilidades_de_competidores_sea_uno(self):
        """
        Metodo encargado de probar la creacion de una carrera en e-porra,
        cuando la suma de las probabilidades de los competidores es diferente
        a uno, se espera que la carrera no sea guardada
        """
        nombre = self.data_factory.name()
        self.nombre_competidor1 = self.data_factory.name()
        self.nombre_competidor2 = self.data_factory.name()

        self.probabilidad_competidor1 = random.uniform(1, 2)
        self.probabilidad_competidor2 = random.uniform(1, 2)

        self.competidor1 = Competidor(
            nombre=self.nombre_competidor1, probabilidad=self.probabilidad_competidor1, ganador=False, carrera=self.carrera)
        self.competidor2 = Competidor(
            nombre=self.nombre_competidor2, probabilidad=self.probabilidad_competidor2, ganador=False, carrera=self.carrera)
        self.session.add(self.competidor1)
        
        competidores = [self.competidor1, self.competidor2]

        with self.assertRaises(Exception):
            self.logica.guardar_cambios_carrera(nombre, competidores, True)

    def test_terminar_carrera_con_ganador_nulo(self):
        """
        Metodo encargado de probar la terminacion de una carrera en e-porra,
        cuando no se coloca un ganador. Se espera que la carrera no sea terminada.
        """
        nombre_ganador = None
        with self.assertRaises(Exception):
            self.logica.terminar_carrera(nombre_ganador)

    def test_terminar_carrera_con_ganador_longitud_cero(self):
        """
        Metodo encargado de probar la terminacion de una carrera en e-porra,
        cuando el nombre del ganador tiene longitud cero. Se espera que la carrera
        """
        nombre_ganador = ""
        with self.assertRaises(Exception):
            self.logica.terminar_carrera(nombre_ganador)

    def test_terminar_carrera_drowdown_muestre_todos_competidores(self):
        '''
        Metodo encargado de probar la terminacion de una carrera en e-porra,  siempre
        que antes se muestre los competidores en el dropdown
        '''
        carrera = self.nombre_carrera
        self.assertEqual(len(self.logica.dar_competidores_carrera(carrera)), 2,
                         "No se deben eliminar competidores al terminar la carrera")

    def test_terminar_carrera_asignacion_ganador_base_datos(self):
        '''
        Metodo encargado de probar que en la terminación de la carrera se cambie el estado del campo ganador de la tabla competidor a True
        '''

        self.logica.terminar_carrera(self.nombre_competidor1)
        competidor = self.session.query(Competidor).filter(
            Competidor.nombre == self.nombre_competidor1).first()
        esGanador = competidor.ganador
        self.assertTrue(
            esGanador, "El competidor no fue asignado como ganador")

    def test_terminar_carrera_cambiar_a_no_abierta(self):
        '''
        Metodo encargado de probar que en la terminación de la carrera se cambie el estado de la carrera a no abierta
        '''
        self.logica.terminar_carrera(self.nombre_competidor1)
        carrera = self.session.query(Carrera).filter(
            Carrera.nombre == self.nombre_carrera).first()
        abierta = carrera.abierta
        self.assertFalse(abierta, "La carrera no fue cerrada")

    def test_generar_reporte_ganancias(self):
        """
        Método encargado para verificar que se crea el reporte con las pruebas
        ganancias y el apostador ganador
        """
        self._popular_datos_reporte()

        lista_ganancias, ganancias_casa = self.logica.dar_reporte_ganancias(self.carrera.nombre, self.competidor1.nombre)
        self.assertEqual(len(lista_ganancias), 2)
        
        cuota = self.competidor1.probabilidad/(1-self.competidor1.probabilidad)
        ganancia_apuesta1 = round(self.valor_apuesta1 + (self.valor_apuesta1  / cuota), 2)
        ganancia_apuesta2 = 0
        ganancia_casa = self.valor_apuesta1 + self.valor_apuesta2 - ganancia_apuesta1 - ganancia_apuesta2
        
        if lista_ganancias[0][0] == self.apuesta1.nombre_apostador:
            self.assertEqual(lista_ganancias[0][1], ganancia_apuesta1)
            self.assertEqual(lista_ganancias[1][1], ganancia_apuesta2)
        else:
            self.assertEqual(lista_ganancias[0][1], ganancia_apuesta2)
            self.assertEqual(lista_ganancias[1][1], ganancia_apuesta1)
        self.assertEqual(ganancias_casa, ganancia_casa)
    
    def test_generar_reporte_ganancias_orden_lista(self):
        """
        Método encargado para verificar que se crea el reporte con las pruebas
        ganancias y el apostador ganador
        """
        self._popular_datos_reporte()

        lista_ganancias, ganancias_casa = self.logica.dar_reporte_ganancias(self.carrera.nombre, self.competidor1.nombre)
        base_apuestas = sorted([self.apuesta1, self.apuesta2], key=lambda ap: ap.nombre_apostador)

        self.assertEqual([g[0] for g in lista_ganancias], [ap.nombre_apostador for ap in base_apuestas])

    def test_eliminar_carrera(self):
        """
        Método encargado de probar la eliminación de una carrera
        """
        resultado = self.logica.eliminar_carrera(self.carrera.nombre)
        carrera = self.session.query(Carrera).filter(
            Competidor.nombre == self.nombre_carrera).first()
        self.assertTrue(resultado, "No se elimino la carrera")
        self.assertIsNone(carrera, "No se elimino la carrera")
        
    def test_eliminar_carrera_con_apuestas(self):
        """
        Método encargado de probar la eliminación de una carrera sin apuestas
        """
        self._popular_datos_reporte()
        resultado = self.logica.eliminar_carrera(self.carrera.nombre)
        carrera = self.session.query(Carrera).filter(
            Competidor.nombre == self.nombre_carrera).first()
        self.assertFalse(resultado, "Se elimino la carrera")