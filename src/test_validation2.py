from app import app
from fastapi.testclient import TestClient

client = TestClient(app)
response = client.get("/api/distributor/0x83C549cC62fEd4798545d945daFB597186981E9c/active-campaign")
print(response.status_code)
print(response.json())
