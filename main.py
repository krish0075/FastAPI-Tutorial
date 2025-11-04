from fastapi import FastAPI
from contextlib import asynccontextmanager
from redis import Redis
import httpx
import json


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis(host="localhost", port=6379)
    app.state.http_client = httpx.AsyncClient()
    yield
    app.state.redis.close()


app = FastAPI(lifespan=lifespan)

@app.get("/entries")
async def read_entries():
    value = app.state.redis.get("entries")
    if value is None:
        response = await app.state.http_client.get("https://api.fda.gov/drug/event.json?limit=1")
        value = response.json()
        data_str = json.dumps(value)
        app.state.redis.set("entries", data_str)
    return json.loads(value)


