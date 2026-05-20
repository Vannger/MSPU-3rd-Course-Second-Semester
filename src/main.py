from fastapi import FastAPI
from src.schemes import UserCreate


app = FastAPI()

@app.post("/registration")
def register_user(user: UserCreate) -> dict:
    return {"msg": "User created", "user": user.username}

