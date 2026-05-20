import re
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

class UserCreate(BaseModel):
    username: str = Field(pattern=r"^[a-zA-Z0-9]+$", min_length=4, max_length=20)
    email: EmailStr
    password: str
    confirm_password: str
    age: int = Field(ge=18, le=100)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if re.search(r"[!@#$%^&*]", v):
            raise ValueError("This password contains at least 1 special symbol")
        if re.search(r"[A-Z]", v):
            raise ValueError("This password contains at least 1 uppercase letter")
        if re.search(r"\d", v):
            raise ValueError("This password contains at least 1 number")
        return v

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'UserCreate':
        if self.password != self.confirm_password:
            raise ValueError("These passwords do not match")
        return self
