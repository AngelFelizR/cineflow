# Cine Flow

Sistema digital para administración de ventas de tickets para cines.

## Planificación

### Creación de User Flow

![](img/04-user-flow.jpg)

### Creaciónde Diagrama Entidad Relación

![](img/05-diagrama-ER.jpg)

## Definición de entorno

### docker-compose

```bash
cat ./docker-compose.yml
services:
  # =======================================================
  # 1. SQL SERVER
  # =======================================================
  mssql2025:
    image: mcr.microsoft.com/mssql/server:2025-RC1-ubuntu-24.04
    container_name: mssql2025
    hostname: mssql2025
    environment:
      ACCEPT_EULA: "Y"
      MSSQL_SA_PASSWORD: "Pass123!"
    ports:
      - "1433:1433"
    networks:
      - dev-network
    volumes:
      - ./cineflow_setup.sql:/tmp/mssql-init.sql
    healthcheck:
      test: >
        /opt/mssql-tools18/bin/sqlcmd
        -S localhost
        -C
        -U sa
        -P Pass123!
        -Q "SELECT 1"
        -b -o /dev/null
      interval: 1s
      timeout: 30s
      retries: 30
      start_period: 20s

  # =======================================================
  # 2. INICIALIZACIÓN DE BASE DE DATOS
  # =======================================================
  mssql-init:
    image: mcr.microsoft.com/mssql-tools:latest
    container_name: mssql-init
    restart: "no"
    depends_on:
      mssql2025:
        condition: service_healthy
    networks:
      - dev-network
    volumes:
      - ./cineflow_setup.sql:/tmp/mssql-init.sql
    command: >
      /bin/sh -c "
        /opt/mssql-tools/bin/sqlcmd -S mssql2025 -U sa -P Pass123! -Q \"IF DB_ID('CineFlow') IS NULL CREATE DATABASE CineFlow\" &&
        until /opt/mssql-tools/bin/sqlcmd -S mssql2025 -U sa -P Pass123! -Q \"SELECT name FROM sys.databases WHERE name='CineFlow'\" | grep -q CineFlow;
        do echo 'Esperando que CineFlow esté disponible...'; sleep 2; done &&
        /opt/mssql-tools/bin/sqlcmd -S mssql2025 -U sa -P Pass123! -d CineFlow -i /tmp/mssql-init.sql
      "

  # =======================================================
  # 3. APLICACIÓN
  # =======================================================
  cineflow:
    build:
      context: .
    container_name: cineflow
    ports:
      - "2224:22"
      - "5000:5000"
    volumes:
      - .:/root/cineflow
    networks:
      - dev-network
    depends_on:
      - mssql-init

networks:
  dev-network:
    driver: bridge
```

### dockerfile

```bash
cat ./Dockerfile
FROM ubuntu:24.04

# Updating the system
RUN apt update -y

# Installing packages to use, including 'xz-utils' for the Nix installer
RUN apt install curl openssh-server xz-utils -y

# The next line install Nix inside Docker
RUN bash -c 'sh <(curl --proto "=https" --tlsv1.2 -L https://nixos.org/nix/install) --daemon'

# Adds Nix to the path
ENV PATH="${PATH}:/nix/var/nix/profiles/default/bin"
ENV user=root

# Install direnv and nix-direnv for Positron integration
RUN nix-env -f '<nixpkgs>' -iA direnv nix-direnv

# Defining enviroment with Nix
COPY default.nix .

# We now build the environment
RUN nix-build

# Defining SSH configuration
RUN mkdir -p /var/run/sshd && \
    echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && \
    echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config

RUN echo 'root:sbs' | chpasswd

# Defining ports to share SSH and App
EXPOSE 22
EXPOSE 5000

# Start SSH server
#CMD ["/usr/sbin/sshd", "-D"]

# Running app and starting ssh server
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
WORKDIR /root/cineflow
CMD ["/entrypoint.sh"]
```


### Dirtree

```bash
tree -L 2
.
├── app.py
├── cineflow_setup.sql
├── config.py
├── controllers
│   ├── boleto_controller.py
│   ├── dashboard_controller.py
│   ├── funcion_controller.py
│   ├── pelicula_controller.py
│   ├── __pycache__
│   └── usuario_controller.py
├── crear_usuarios_hash.py
├── crear_usuarios_hash.sql
├── database.py
├── default.nix
├── diagramas
│   ├── Entidad Relación - Cine Flow.drawio.pdf
│   ├── User Flow - Administrador.drawio.pdf
│   ├── User Flow - Cliente.drawio.pdf
│   └── User Flow - Encargado de Entrada.drawio.pdf
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── img
│   ├── 01-trust-files
│   ├── 02-allow-dir-env.jpg
│   └── 03-install-dir-env.jpg
├── models.py
├── __pycache__
│   ├── config.cpython-313.pyc
│   ├── database.cpython-313.pyc
│   └── models.cpython-313.pyc
├── README.md
├── static
│   ├── css
│   └── js
└── templates
    ├── admin_dashboard.html
    ├── asiento
    ├── base.html
    ├── boleto
    ├── boleto_cancelado
    ├── boletos
    ├── boleto_usado
    ├── cine
    ├── clasificacion
    ├── funcion
    ├── funciones
    ├── genero
    ├── idioma
    ├── index.html
    ├── pelicula
    ├── pelicula_genero
    ├── peliculas
    ├── rol_usuario
    ├── sala
    ├── tipo_boleto
    ├── tipo_sala
    └── usuario
```

## Como correr la applicación

```bash
docker compose up -d --build
```

**localhost:5000**
