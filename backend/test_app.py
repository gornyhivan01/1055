import pytest
from unittest.mock import MagicMock, patch
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.celery')
def test_check_url_success(mock_celery, client):
    # Мокируем Celery-задачу
    mock_task = MagicMock()
    mock_task.id = 'test-task-id'
    mock_celery.send_task.return_value = mock_task

    response = client.post('/api/check', json={'url': 'http://example.com'})

    assert response.status_code == 202
    data = response.get_json()
    assert data['task_id'] == 'test-task-id'
    mock_celery.send_task.assert_called_once_with('tasks.check_availability', args=['http://example.com'])

@patch('app.celery')
def test_check_url_missing_url(mock_celery, client):
    response = client.post('/api/check', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

@patch('app.celery')
def test_get_status(mock_celery, client):
    mock_result = MagicMock()
    mock_result.status = 'SUCCESS'
    mock_result.result = True
    mock_celery.AsyncResult.return_value = mock_result

    response = client.get('/api/status/test-task-id')

    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'SUCCESS'
    assert data['result'] is True
    mock_celery.AsyncResult.assert_called_once_with('test-task-id')