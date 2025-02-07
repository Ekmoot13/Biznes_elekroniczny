IMAGE_NAME="ekmoot13/worsted:latest"
COMPOSE_URL="https://raw.githubusercontent.com/Ekmoot13/Biznes_elekroniczny/TESTS/docker-compose.yml"
STACK_NAME="BE_188893"

docker pull $IMAGE_NAME

wget $COMPOSE_URL -O docker-compose-prod.yml

sed -i -e 's/\r$//' ./docker-compose-prod.yml

docker stack deploy -c docker-compose-prod.yml $STACK_NAME --with-registry-auth
