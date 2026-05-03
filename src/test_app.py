from app import app
from fastapi.testclient import TestClient

client = TestClient(app)
response = client.get("/check-user?address=0x83C549cC62fEd4798545d945daFB597186981E9c")
print(response.status_code)
print(response.text)
