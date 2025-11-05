from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String
from database import SessionLocal, engine, Base
from contextlib import asynccontextmanager
from redis import Redis
import httpx
import json
import uuid
from pydantic import UUID4, BaseModel, Field, EmailStr


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis(host="localhost", port=6379)
    app.state.http_client = httpx.AsyncClient()
    yield
    app.state.redis.close()


app = FastAPI(lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create Table model
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

Base.metadata.create_all(engine)


class CreateUser(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=12)
    age: int = Field(gt=21)


class UserModel(CreateUser):
    id: UUID4 = Field(default_factory=uuid.uuid4)


@app.post("/user")
def fetch_user(user: CreateUser):
    user = UserModel(email=user.email, password=user.password, age=user.age)
    return user


@app.post("/users")
def add_user(name: str, email: str, db: Session = Depends(get_db)):
    user = User(name=name, email=email)
    db.add(user)
    db.commit()


@app.get("/users")
def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@app.get("/entries")
async def read_entries():
    value = app.state.redis.get("entries")
    if value is None:
        response = await app.state.http_client.get("https://api.fda.gov/drug/event.json?limit=1")
        value = response.json()
        data_str = json.dumps(value)
        app.state.redis.set("entries", data_str)
    return json.loads(value)
