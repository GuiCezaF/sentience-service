def test_health_check(client):
    """
    Test Case: Success
    Verify that the health check route returns OK.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
