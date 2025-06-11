import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock

from src.app.api.main import app
from src.db import get_db
from src.app.api.v1 import dependencies


@pytest.fixture
def db_session() -> MagicMock:
    """
    Yields a MagicMock object for the database session.
    Resets the mock after the test.
    """
    db = MagicMock(spec=Session)
    yield db
    db.reset_mock()


@pytest.fixture
def client(db_session: MagicMock) -> TestClient:
    """
    Yields a TestClient with the database and auth dependencies overridden.
    """

    def override_get_db():
        yield db_session

    def override_api_token_auth():
        pass

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[dependencies.api_token_auth] = override_api_token_auth

    with TestClient(app) as c:
        yield c

    # Clean up dependency overrides after tests
    app.dependency_overrides.clear()
