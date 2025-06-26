# app/models/user.py

from beanie import Document
from pydantic import EmailStr
from typing import Literal

class User(Document):
    email: EmailStr
    name: str
    role: Literal["customer", "restaurant"] = "customer"  # default
    google_id: str

    class Settings:
        name = "users"
