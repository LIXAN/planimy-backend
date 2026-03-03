from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
response = client.post("/auth/login", data={"username": "admin@saas.com", "password": "password123"})
print(response.status_code)
print(response.json())
