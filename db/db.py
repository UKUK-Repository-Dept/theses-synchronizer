from db import *

__all__ = ['reflect']


def reflect(engine):
    Base = declarative_base()
    metadata = MetaData(bind=engine, schema='STDOWNER')

    metadata.reflect(views=True)

    return metadata
