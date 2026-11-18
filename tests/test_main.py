from conftest import test_client

def test_get_root(test_client):
    response = test_client.get(f"/")
    assert response.status_code == 200