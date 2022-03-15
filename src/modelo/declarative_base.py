from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

E_PORRA_ADDRESS = 'sqlite:///aplicacion.sqlite'
TESTING_ADDRESS = 'sqlite:///aplicacion_test.sqlite'

Base = declarative_base()

def crear_session(address):
    engine = create_engine(address)
    Session = sessionmaker(bind=engine)
    return (engine, Session())
