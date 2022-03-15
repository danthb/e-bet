import sys
from PyQt5.QtWidgets import QApplication
from src.vista.InterfazEPorra import App_EPorra
from src.logica.Logica_mock import Logica_mock
from src.logica.manager_eporra import ManagerEPorra
from src.modelo.declarative_base import E_PORRA_ADDRESS

if __name__ == '__main__':
    # Punto inicial de la aplicación

    logica = Logica_mock()
    manager_eporra = ManagerEPorra(E_PORRA_ADDRESS)

    app = App_EPorra(sys.argv, manager_eporra)
    sys.exit(app.exec_())