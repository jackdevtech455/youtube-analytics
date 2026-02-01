from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from yta_core.settings import CoreSettings

core_settings = CoreSettings()

engine = create_engine(str(core_settings.database_url), pool_pre_ping=True)
SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
