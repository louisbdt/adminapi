import os
import requests

NETBOX_URL = os.environ.get("NETBOX_URL", "http://127.0.0.1:8080")
NETBOX_TOKEN = os.environ["NETBOX_TOKEN"]

netbox = requests.Session()
netbox.headers["Authorization"] = f"Bearer {NETBOX_TOKEN}"

N = f"{NETBOX_URL}/api/virtualization"

def id_cluster_docker_local():
    reponse = netbox.get(f"{N}/clusters/", params={"name": "docker-local"}, timeout=10)
    reponse.raise_for_status()
    return reponse.json()["results"][0]["id"]