from diagrams import Diagram
from diagrams.c4 import Person, Container, System, Relationship, SystemBoundary

graph_attr = {
    "splines": "spline",
}

with Diagram("02 - Container Diagram - Sistema de Gestión de Cine", direction="TB", graph_attr=graph_attr):
    
    # Actores externos
    customer = Person(
        name="Cliente",
        description="Persona que accede al sistema para consultar funciones y comprar entradas."
    )
    
    admin = Person(
        name="Administrador",
        description="Usuario responsable de la gestión de películas, funciones y cartelera."
    )
    
    # Sistemas externos
    youtube = System(
        name="YouTube",
        description="Plataforma externa para reproducir trailers de películas",
        external=True
    )
    
    payment_gateway = System(
        name="Payment Gateway (Mock)",
        description="Simulador de pasarela de pago para procesar transacciones",
        external=True
    )
    
    # Boundary del sistema
    with SystemBoundary("Sistema Web de Cine"):
        
        # Frontend
        frontend = Container(
            name="Aplicación Web",
            technology="Bootstrap 5, HTML, CSS, JS",
            description="Interfaz de usuario para clientes y administradores. Maneja cookies de sesión y consume API REST."
        )
        
        # Backend
        backend = Container(
            name="API Backend",
            technology="Flask, Flask-Session, SQLAlchemy ORM",
            description="API REST que maneja lógica de negocio, autenticación, autorización y gestión de sesiones."
        )
        
        # Base de datos
        database = Container(
            name="Base de Datos",
            technology="SQL Server 2025",
            description="Almacena usuarios, roles, películas, funciones, salas, ventas y asientos."
        )
        
        # Almacenamiento de archivos
        file_storage = Container(
            name="Almacenamiento de Imágenes",
            technology="Local File System",
            description="Almacena pósters y imágenes de películas."
        )
        
        # Assets estáticos
        static_assets = Container(
            name="Assets Estáticos",
            technology="Bootstrap 5 (local), CSS, JS",
            description="Archivos estáticos descargados localmente: Bootstrap, librerías JS, CSS custom."
        )
    
    # Relaciones - Usuarios a Frontend
    customer >> Relationship("Consulta cartelera y compra entradas [HTTPS + Cookies]") >> frontend
    admin >> Relationship("Administra el sistema [HTTPS + Cookies]") >> frontend
    
    # Relaciones - Frontend a Backend
    frontend >> Relationship("Hace llamadas API con cookie de sesión [JSON/HTTPS]") >> backend
    frontend >> Relationship("Carga recursos estáticos") >> static_assets
    frontend >> Relationship("Embebe trailers [YouTube iframe API]") >> youtube
    
    # Relaciones - Backend a Base de Datos
    backend >> Relationship("Lee/Escribe datos [SQL]") >> database
    backend >> Relationship("Sube/Descarga imágenes [FileSystem]") >> file_storage
    
    # Relaciones - Backend a sistemas externos
    backend >> Relationship("Procesa pagos [HTTPS/REST API]") >> payment_gateway