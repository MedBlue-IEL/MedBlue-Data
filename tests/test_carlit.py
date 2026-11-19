from conftest import test_client

def test_get_all_carlit(test_client):
    response = test_client.get(f"/carlit/")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0

def test_get_carlit_by_id(test_client):
    response = test_client.get(f"/carlit/1")
    assert response.status_code == 200