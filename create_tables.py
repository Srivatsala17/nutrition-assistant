from db.database import engine, Base
from db import models  # noqa: F401  (needed so tables are registered)

Base.metadata.create_all(engine)
print("Tables created!")

