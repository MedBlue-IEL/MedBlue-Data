from conftest import test_client

def test_get_all_species(test_client):
    response = test_client.get(f"/species/")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0