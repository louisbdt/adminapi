# TP1 : exploration

## API Docker

### Version
`curl -s $D/version`
→ 200, Docker Engine 28.0.1, API version 1.48

### Liste de tous les conteneurs
`curl -s "$D/containers/json?all=true"`
→ 6 conteneurs : intrus, web1, apirest-netbox-1, apirest-docker-api-1, apirest-netbox-postgres-1, apirest-netbox-redis-1
→ tous les conteneurs de la machine, pas seulement les miens

### Liste filtrée par label
`curl -s --get $D/containers/json --data-urlencode 'all=true' --data-urlencode 'filters={"label":["adminapi.managed=true"]}'`
→ un seul résultat : web1 (le seul avec le label `adminapi.managed=true`)

### Détail de web1
`curl -s $D/containers/web1/json`
→ "Id": "35c9eed931bf...", "Name": "/web1", "Config.Labels": {"adminapi.managed": "true", ...}, "State.Status": "running"

### Arrêt de web1 (x2) + conteneur inconnu
- `curl -i -X POST $D/containers/web1/stop` → **204 No Content**
- `curl -i -X POST $D/containers/web1/stop` → **304 Not Modified**
- `curl -i -X POST $D/containers/nexistepas/stop` → **404 Not Found**, `{"message":"No such container: nexistepas"}`

## API NetBox

### Token
`curl -s -X POST $N/users/tokens/provision/ ...`
→ 200, token récupéré et stocké dans `.env` (format `nbt_<key>.<token>`)

### Type de cluster
`curl -s -X POST $N/virtualization/cluster-types/ -H "$A" -d '{"name": "Docker", "slug": "docker"}'`
→ 200, créé avec `"id": 1`

### Cluster
`curl -s -X POST $N/virtualization/clusters/ -H "$A" -d '{"name": "docker-local", "type": 1}'`
→ 200, créé avec `"id": 1`, statut `active`, rattaché au type `Docker`
