from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

# Configure SQLAlchemy to log all queries
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

DATABASE_URL = 'mysql+mysqldb://root:hana2001@localhost/cartdb'

Base = declarative_base()

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db_session = Session()
