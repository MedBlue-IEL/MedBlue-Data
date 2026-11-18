from conftest import test_client

def test_get_all_habitats(test_client):
    response = test_client.get(f"/habitats/")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0