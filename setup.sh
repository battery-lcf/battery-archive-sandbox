## Copyright 2021 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.
rm env 

COOKIE_SECRET=$(pwgen -1s 32)
SECRET_KEY=$(pwgen -1s 32)
POSTGRES_PASSWORD=$(pwgen -1s 32)
REDASH_DATABASE_URL="postgresql://postgres:${POSTGRES_PASSWORD}@postgres/postgres"
DATABASE_CONNECTION="postgresql://postgres:${POSTGRES_PASSWORD}@localhost:5432/postgres"
PGADMIN4_PASSWORD=$(pwgen -1s 32)

echo "PYTHONUNBUFFERED=0" >> env
echo "REDASH_LOG_LEVEL=INFO" >> env
echo "REDASH_REDIS_URL=redis://redis:6379/0" >> env
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" >> env
echo "REDASH_COOKIE_SECRET=$COOKIE_SECRET" >> env
echo "REDASH_SECRET_KEY=$SECRET_KEY" >> env
echo "REDASH_DATABASE_URL=$REDASH_DATABASE_URL" >> env
echo "DATABASE_CONNECTION=$DATABASE_CONNECTION" >> env
echo "PGADMIN_DEFAULT_EMAIL=user@pgadmin4.web" >> env
echo "PGADMIN_DEFAULT_PASSWORD=$PGADMIN4_PASSWORD" >> env

sudo docker-compose run --rm server create_db
sudo docker-compose up -d 
