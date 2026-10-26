import json
import os
from datetime import datetime
import requests
import sys

DOCKER = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")
NETBOX = os.environ.get("NETBOX_URL", "http://127.0.0.1:8080")
NETBOX_TOKEN = os.environ["NETBOX_TOKEN"]


def lister_conteneurs(session):
    response = session.get(DOCKER + '/containers/json',  params={"all": "true"}, timeout =5)
    response.raise_for_status()
    response = response.json()

    result = []
    for r in response:
        conteneur = {"id": r["Id"], "name": r["Names"][0].lstrip("/"), "image": r["Image"], "state": r["State"]}
        if r["State"] == "running":
            stats = recuperer_stats(session, r["Id"])
            conteneur = conteneur | stats
        result.append(conteneur)
    return result


def recuperer_stats(session, conteneur_id):
    response = session.get(DOCKER + '/containers/' + conteneur_id + '/stats'
                , params={"stream": "false"}
                , timeout=5)
    response.raise_for_status()
    stats = response.json()

    cpu, avant = stats["cpu_stats"], stats["precpu_stats"]
    delta_cpu = cpu["cpu_usage"]["total_usage"] - avant["cpu_usage"]["total_usage"]
    delta_systeme = cpu["system_cpu_usage"] - avant.get("system_cpu_usage", 0)
    pourcent = delta_cpu / delta_systeme * cpu["online_cpus"] * 100 if delta_systeme else 0.0

    memoire_mo = stats["memory_stats"]["usage"] / 1024 / 1024

    return {"cpu_percent": pourcent, "memoire_mo": memoire_mo}


def recuperer_netbox(session):
    headers = {"Authorization": f"Bearer {NETBOX_TOKEN}"}

    response = session.get(NETBOX + '/api/status/', headers=headers, timeout=5)
    response.raise_for_status()
    version = response.json()["netbox-version"]

    url = NETBOX + "/api/core/object-types/?limit=50"
    compteur = 0
    while url:
        response = session.get(url, headers=headers, timeout=5).json()
        compteur += len(response["results"])
        url = response["next"]

    return {"netbox_version": version, "nombre_types_objets": compteur}


if __name__ == "__main__":
    try:
        session = requests.Session()
        conteneurs = lister_conteneurs(session)
        netbox = recuperer_netbox(session)
        inventaire = {"date": datetime.now().isoformat(), "conteneurs": conteneurs} | netbox

        with open("inventaire.json", 'w') as f:
            json.dump(inventaire, f, indent=2)

        compteurs = {}
        for c in conteneurs:
            etat = c["state"]
            compteurs[etat] = compteurs.get(etat, 0) + 1
        print(f"{len(conteneurs)} conteneurs : {compteurs}")
    except requests.exceptions.RequestException as erreur:
        sys.exit(f"Erreur : impossible de contacter une des API ({erreur})")