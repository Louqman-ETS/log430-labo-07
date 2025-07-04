import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Override database configuration before importing app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from main import app
from src.database import get_db, engine
from src.models import Base

# Create tables in the test database
Base.metadata.create_all(bind=engine)

@pytest.fixture
def client():
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client 