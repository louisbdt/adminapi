from fastapi import FastAPI
import os
import requests
import json

DOCKER = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")

app = FastAPI()


@app.get("/health")
async def root():
    return {"status": "ok"}

@app.get("/containers")
async def getContainers():
    response = requests.get(DOCKER + "/containers/json", params={
    "all": "true",
    "filters": '{"label":["adminapi.managed=true"]}'
}, timeout=5)
    response.raise_for_status()
    response = response.json()

    result = []
    for r in response:
        conteneur = {"id": r["Id"], "name": r["Names"][0].lstrip("/"), "image": r["Image"], "state": r["State"]}
        result.append(conteneur)
    return result
    