import json
import os
import requests

DOCKER = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")


def lister_conteneurs(session):
    response = session.get(DOCKER + '/containers/json',  params={"all": "true"}, timeout =5)
    response.raise_for_status()
    response = response.json()

    result = []
    for r in response :
        result.append({"id": r["Id"], "name": r["Names"][0].lstrip("/"), "image": r["Image"], "state": r["State"]})
    return result


if __name__ == "__main__":
    session = requests.Session()
    conteneurs = lister_conteneurs(session)
    print(json.dumps(conteneurs, indent=2))
