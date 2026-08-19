import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Force an isolated test database before importing the app
os.environ["DATABASE_URL"] = "sqlite:///./test_smart_farming.db"

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_smart_farming.db"):
        os.remove("test_smart_farming.db")


@pytest.fixture()
def client():
    return TestClient(app)
