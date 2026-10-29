#!/usr/bin/env bash
# Deploys a local Wazuh single-node lab (manager + indexer + dashboard) with Docker.
# Admin ports (API 55000, indexer 9200, dashboard 443) are bound to 127.0.0.1 only,
# because the upstream compose ships with well-known default passwords.
set -euo pipefail

WAZUH_VERSION="${WAZUH_VERSION:-4.14.7}"
LAB_DIR="${LAB_DIR:-$(dirname "$0")/wazuh-docker}"

if [[ ! -d "$LAB_DIR" ]]; then
  git clone --depth 1 -b "v${WAZUH_VERSION}" https://github.com/wazuh/wazuh-docker.git "$LAB_DIR"
fi

cd "$LAB_DIR/single-node"

# Bind admin ports to localhost. Agent ports (1514/1515) stay open so remote agents can enroll.
sed -i \
  -e 's|- "55000:55000"|- "127.0.0.1:55000:55000"|' \
  -e 's|- "9200:9200"|- "127.0.0.1:9200:9200"|' \
  -e 's|- 443:5601|- "127.0.0.1:443:5601"|' \
  docker-compose.yml

if [[ ! -f config/wazuh_indexer_ssl_certs/root-ca.pem ]]; then
  docker compose -f generate-indexer-certs.yml run --rm generator
fi

docker compose up -d
echo "Wazuh lab starting. Dashboard: https://localhost  API: https://localhost:55000  Indexer: https://localhost:9200"
