import pytest

from app import app


@pytest.fixture(scope='session')
def client():
    app.testing = True
    return app.test_client()
