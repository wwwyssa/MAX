import requests

ans = requests.get("https://https://platform-api.max.ru/me", headers={"Authorization": "f9LHodD0cOIRY0kxaAAsvfhYqEv2ley3x9B2T7Mn6JIxw7Y6i5U8Wu1eMGbWXUNk1menHVRnTDdwyLRUe6mA"})

print(ans)