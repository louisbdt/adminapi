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
        result.append({"id": r["Id"], "name": r["Names"][0].lstrip("/"), "image": r["Image"], "state": r["State"]} | stats)
        if r["State"] == "running" : 
            stats = recuperer_stats(session, r["Id"])
            result.append(stats)
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


if __name__ == "__main__":
    session = requests.Session()
    stats = recuperer_stats(session, "4c21cc5bf2fdd11d24aa3c6de764a6db7aad971fbbdfdeb0279603a4af900a83")
    print(json.dumps(stats, indent=2))
