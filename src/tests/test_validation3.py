from app import app
from fastapi.testclient import TestClient

client = TestClient(app)
print("Testing /api/campaigns")
response = client.get("/api/campaigns")
print(response.status_code)
