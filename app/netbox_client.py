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

def creer_vm(nom, id_cluster):
    reponse = netbox.post(f"{N}/virtual-machines/", timeout=10,
                           json={"name": nom, "cluster": id_cluster, "status": "active"})
    reponse.raise_for_status()
    return reponse.json()

def trouver_vm(nom, id_cluster):
    reponse = netbox.get(f"{N}/virtual-machines/", timeout=10,
                          params={"name": nom, "cluster_id": id_cluster})
    reponse.raise_for_status()
    resultats = reponse.json()["results"]
    return resultats[0] if resultats else None

def changer_statut_vm(id_vm, statut):
    netbox.patch(f"{N}/virtual-machines/{id_vm}/", json={"status": statut}, timeout=10).raise_for_status()

def supprimer_vm(id_vm):
    netbox.delete(f"{N}/virtual-machines/{id_vm}/", timeout=10).raise_for_status()