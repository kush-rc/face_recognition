import bcrypt
import json

users = [
    {
        "username": "admin",
        "password": bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode(),
        "role": "admin"
    },
    {
        "username": "john",
        "password": bcrypt.hashpw("john123".encode(), bcrypt.gensalt()).decode(),
        "role": "user"
    }
]

with open("user.json", "w") as f:
    json.dump(users, f, indent=2)

print("✅ user.json created with hashed passwords!")
