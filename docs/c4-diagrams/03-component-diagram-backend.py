from diagrams import Diagram, Cluster
from diagrams.c4 import Person, Container, System, Relationship, SystemBoundary

graph_attr = {
    "splines": "spline",
    "nodesep": "0.8",
    "ranksep": "1.2",
}

with Diagram("03 - Component Diagram - Backend Sistema de Gestion de Cine", 
             direction="TB", 
             graph_attr=graph_attr,
             show=False):
    
    # Containers externos al Backend
    frontend = Container(
        name="Aplicacion Web",
        technology="Bootstrap 5, HTML, CSS, JS",
        description="Frontend que consume la API"
    )
    
    database = Container(
        name="Base de Datos",
        technology="SQL Server 2025",
        description="Almacena toda la informacion"
    )
    
    file_storage = Container(
        name="File Storage",
        technology="Local FileSystem",
        description="Imagenes de peliculas"
    )
    
    payment_gateway = System(
        name="Payment Gateway (Mock)",
        description="Simulador de pagos - Mock API",
        external=True
    )
    
    # Backend Component Diagram
    with SystemBoundary("API Backend - Flask"):
        
        # ===== CONTROLLERS (MVC Pattern) - INDIVIDUALES =====
        with Cluster("Controllers Layer (Flask Blueprints)"):
            auth_controller = System(
                name="Auth Controller",
                description="Login, logout, registro"
            )
            
            movie_controller = System(
                name="Movie Controller",
                description="CRUD peliculas"
            )
            
            function_controller = System(
                name="Function Controller",
                description="CRUD funciones"
            )
            
            booking_controller = System(
                name="Booking Controller",
                description="Venta boletos"
            )
            
            client_controller = System(
                name="Client Controller",
                description="CRUD clientes"
            )
            
            report_controller = System(
                name="Report Controller",
                description="3+ reportes"
            )
            
            genre_controller = System(
                name="Genre Controller",
                description="CRUD generos"
            )
            
            sala_controller = System(
                name="Sala Controller",
                description="CRUD salas"
            )
        
        # ===== SERVICES (Business Logic) - PRINCIPALES + AGRUPADOS =====
        with Cluster("Business Logic Layer"):
            # Services principales (los críticos para el negocio)
            auth_service = System(
                name="Authentication Service",
                description="Valida credenciales, maneja roles (cliente/admin)"
            )
            
            booking_service = System(
                name="Booking Service",
                description="Logica reserva, calculo precios, asientos"
            )
            
            report_service = System(
                name="Report Generator",
                description="Reportes: peliculas vistas, ocupacion, ventas (joins/agregaciones)"
            )
            
            # Services de soporte agrupados
            support_services = System(
                name="Support Services",
                description="Validation, Payment, QR Generator, Seat Manager, Genre, Sala"
            )
        
        # ===== MODELS (ORM - SQLAlchemy) =====
        with Cluster("Data Access Layer (ORM)"):
            models = System(
                name="SQLAlchemy Models",
                description="6+ tablas: Pelicula, Sala, Funcion, Cliente, Boleto, Genero\n(relaciones 1:N y N:M)"
            )
            
            db_session = System(
                name="DB Session Manager",
                description="Gestiona conexiones, transacciones, rollback"
            )
        
        # ===== UTILITIES =====
        with Cluster("Utilities Layer"):
            utilities = System(
                name="Cross-cutting Utilities",
                description="Error Handler, Flash Messages, Session Manager, File Handler"
            )
    
    # ===== RELACIONES SIMPLIFICADAS PERO CLARAS =====
    
    # Frontend -> Controllers (agrupado visualmente pero muestra todos)
    frontend >> Relationship("API REST [JSON/HTTPS]") >> auth_controller
    frontend >> Relationship("") >> movie_controller
    frontend >> Relationship("") >> function_controller
    frontend >> Relationship("") >> booking_controller
    frontend >> Relationship("") >> client_controller
    frontend >> Relationship("") >> report_controller
    frontend >> Relationship("") >> genre_controller
    frontend >> Relationship("") >> sala_controller
    
    # Controllers -> Services (solo las principales)
    auth_controller >> Relationship("valida") >> auth_service
    booking_controller >> Relationship("procesa venta") >> booking_service
    report_controller >> Relationship("genera reportes") >> report_service
    
    # Controllers -> Support Services (agrupado)
    movie_controller >> Relationship("valida/procesa") >> support_services
    function_controller >> Relationship("valida horarios") >> support_services
    genre_controller >> Relationship("gestiona") >> support_services
    sala_controller >> Relationship("gestiona") >> support_services
    
    # All Controllers -> Utilities (una flecha representativa)
    auth_controller >> Relationship("usan") >> utilities
    
    # Services -> Models
    auth_service >> Relationship("CRUD usuarios") >> models
    booking_service >> Relationship("CRUD boletos/asientos") >> models
    report_service >> Relationship("queries complejas") >> models
    support_services >> Relationship("CRUD general") >> models
    
    # Models -> Database
    models >> Relationship("ORM mapping") >> db_session
    db_session >> Relationship("SQL queries") >> database
    
    # External integrations
    support_services >> Relationship("procesa pagos") >> payment_gateway
    utilities >> Relationship("maneja archivos") >> file_storage