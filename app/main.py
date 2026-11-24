from fastapi import FastAPI, HTTPException
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

@app.get("/containers/{id}")
async def getContainer(id: str):
    response = requests.get(DOCKER + f"/containers/{id}/json", timeout=5)
    if response.status_code == 404:
        raise HTTPException(status_code=404)
    response.raise_for_status()
    data = response.json()

    labels = data["Config"]["Labels"] or {}
    if labels.get("adminapi.managed") != "true":
        raise HTTPException(status_code=404)

    return {
        "id": data["Id"],
        "name": data["Name"].lstrip("/"),
        "image": data["Config"]["Image"],
        "state": data["State"]["Status"],
    }