import pytest

from app import app
from app.routes import API_PREFIX


@pytest.fixture(scope='session')
def client():
    app.testing = True
    return app.test_client()


@pytest.fixture
def single_patient(client):
    """
    Create patient, yield id, and delete
    """
    body = {
        'first_name': 'foo',
        'last_name': 'bar'
    }
    result = client.post(f'{API_PREFIX}/patients', data=body)
    assert result.status_code == 201

    patient_id = int(result.headers['Location'].split('/')[-1])
    yield patient_id

    result = client.delete(f'{API_PREFIX}/patients/{patient_id}')
    assert result.status_code == 204


@pytest.fixture
def single_provider(client):
    """
    Create provider, yield id, and delete
    """
    body = {
        'first_name': 'doc',
        'last_name': 'tor'
    }
    result = client.post(f'{API_PREFIX}/providers', data=body)
    assert result.status_code == 201

    provider_id = int(result.headers['Location'].split('/')[-1])
    yield provider_id

    result = client.delete(f'{API_PREFIX}/providers/{provider_id}')
    assert result.status_code == 204
