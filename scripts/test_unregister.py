from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

activity = "Chess Club"
email = "michael@mergington.edu"

print('Before:', activities[activity]['participants'])
resp = client.post(f"/activities/{activity}/unregister?email={email}")
print('Status code:', resp.status_code)
print('Response:', resp.json())
print('After:', activities[activity]['participants'])

# revert change so tests are idempotent
if resp.status_code == 200 and email not in activities[activity]['participants']:
    activities[activity]['participants'].append(email)
    print('Reverted change')
else:
    print('No revert needed')
