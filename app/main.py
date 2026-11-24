from fastapi import FastAPI, HTTPException
import os
import requests
import json
from typing import Literal
from pydantic import BaseModel, Field

DOCKER = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")

app = FastAPI()


Image = Literal["nginx:alpine", "redis:alpine", "httpd:alpine"]


class ConteneurACreer(BaseModel):
    name: str = Field(pattern=r"^[a-z][a-z0-9-]{1,30}$")
    image: Image


def get_managed_container(id: str) -> dict:
    response = requests.get(DOCKER + f"/containers/{id}/json", timeout=5)
    if response.status_code == 404:
        raise HTTPException(status_code=404)
    response.raise_for_status()
    data = response.json()

    labels = data["Config"]["Labels"] or {}
    if labels.get("adminapi.managed") != "true":
        raise HTTPException(status_code=404)

    return data

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

@app.post("/containers", status_code=201)
async def creerConteneur(demande: ConteneurACreer):
    corps = {"Image": demande.image, "Labels": {"adminapi.managed": "true"}}
    response = requests.post(
        DOCKER + "/containers/create",
        params={"name": demande.name},
        json=corps,
        timeout=10,
    )
    if response.status_code == 409:
        raise HTTPException(status_code=409)
    response.raise_for_status()
    id = response.json()["Id"]

    requests.post(DOCKER + f"/containers/{id}/start", timeout=10).raise_for_status()

    data = requests.get(DOCKER + f"/containers/{id}/json", timeout=5).json()
    return {
        "id": data["Id"],
        "name": data["Name"].lstrip("/"),
        "image": data["Config"]["Image"],
        "state": data["State"]["Status"],
    }

@app.post("/containers/{id}/stop")
async def arreterConteneur(id: str):
    get_managed_container(id)
    response = requests.post(DOCKER + f"/containers/{id}/stop", params={"t": 2}, timeout=30)
    if response.status_code == 304:
        raise HTTPException(status_code=409)
    response.raise_for_status()

    data = requests.get(DOCKER + f"/containers/{id}/json", timeout=5).json()
    return {
        "id": data["Id"],
        "name": data["Name"].lstrip("/"),
        "image": data["Config"]["Image"],
        "state": data["State"]["Status"],
    }


@app.post("/containers/{id}/start")
async def demarrerConteneur(id: str):
    get_managed_container(id)
    response = requests.post(DOCKER + f"/containers/{id}/start", timeout=10)
    if response.status_code == 304:
        raise HTTPException(status_code=409)
    response.raise_for_status()

    data = requests.get(DOCKER + f"/containers/{id}/json", timeout=5).json()
    return {
        "id": data["Id"],
        "name": data["Name"].lstrip("/"),
        "image": data["Config"]["Image"],
        "state": data["State"]["Status"],
    }