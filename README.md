# Cine Flow

Sistema digital para administración de ventas de tickets para cines.


## Descripción de funcionalidades


## Como correr la applicación

Para correr la aplicación se necesita tener docker instalado y correr el siguiente comando desde la terminal.

```bash
docker compose up -d --build
```

Con este solo comando se realizar las siguientes acciones:

1. Se inicia el contenedor con la base de Datos SQL Server 2025 desde la imagen de ubuntu.
2. Se configura la base de datos según lo indicado en `cineflow_setup.sql`
3. Se activa el contenedor donde correrá la aplicación exponiendo los puertos `2224` y `5001` para la conexión ssh y el despligue de la aplicación respectivamente.

**Nota:** No estamos creando volúmenes en la base de datos ya que en esta etapa no necetamos almacenar los datos de las interacciones, pero en caso de que se quieran mantener los datos de los cambios aplicados se puede editar el `docker-compose.yml` de la siguiente manera.

```bash
services
  mssql2025:
    image: mcr.microsoft.com/mssql/server:2025-RC1-ubuntu-24.04
    container_name: mssql2025
    hostname: mssql2025
    environment:
      - ACCEPT_EULA=Y
      - MSSQL_SA_PASSWORD=Pass123!
    ports:
      - "1433:1433"
    volumes:
      # We need to define correct permitons for folders
      # - sudo chown -R 10001:10001 mssql2025/data
      # - sudo chown -R 10001:10001 mssql2025/log
      # - sudo chown -R 10001:10001 mssql2025/secrets
      - ./mssql2025/data:/var/opt/mssql/data
      - ./mssql2025/log:/var/opt/mssql/log
      - ./mssql2025/secrets:/var/opt/mssql/secrets
    networks:
      - dev-network
```

Para confirmar si efectivamente la base de datos fue creada podemos correr el siguiente comando desde la terminal

```bash
docker run --rm -it \
  --network cineflow_dev-network \
  mcr.microsoft.com/mssql-tools \
  /opt/mssql-tools/bin/sqlcmd \
   -S mssql2025 \
   -U sa \
   -P Pass123! \
   -Q "SELECT name FROM sys.databases"
```
