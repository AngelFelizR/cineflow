from diagrams import Diagram, Cluster
from diagrams.c4 import Person, Container, System, Relationship, SystemBoundary

graph_attr = {
    "splines": "spline",
    "nodesep": "0.8",
    "ranksep": "1.2",
}

with Diagram("04 - Component Diagram - Frontend Sistema de Gestion de Cine", 
             direction="TB", 
             graph_attr=graph_attr,
             show=False):
    
    # Actores
    customer = Person(
        name="Cliente",
        description="Usuario que compra entradas"
    )
    
    admin = Person(
        name="Administrador",
        description="Gestiona peliculas y funciones"
    )
    
    # Containers externos al Frontend
    backend = Container(
        name="API Backend",
        technology="Flask REST API",
        description="Provee endpoints REST"
    )
    
    static_assets = Container(
        name="Static Assets",
        technology="Bootstrap 5, CSS, JS",
        description="Recursos estaticos"
    )
    
    youtube = System(
        name="YouTube",
        description="Plataforma de trailers",
        external=True
    )
    
    # Frontend Component Diagram
    with SystemBoundary("Aplicacion Web (Frontend)"):
        
        # ===== TEMPLATES (Views) - Jinja2 =====
        with Cluster("Templates Layer (Jinja2)"):
            
            # Template base
            base_template = System(
                name="base.html",
                description="Template base: navbar, footer, includes Bootstrap/CSS"
            )
            
            # Templates por módulo
            auth_templates = System(
                name="Auth Templates",
                description="login.html, register.html - Formularios autenticacion"
            )
            
            movie_templates = System(
                name="Movie Templates",
                description="movies/lista.html, nuevo.html, editar.html - CRUD peliculas"
            )
            
            function_templates = System(
                name="Function Templates",
                description="functions/lista.html, nuevo.html - Programacion funciones"
            )
            
            booking_templates = System(
                name="Booking Templates",
                description="bookings/seleccion_asientos.html, confirmar.html - Compra boletos"
            )
            
            admin_templates = System(
                name="Admin Dashboard",
                description="admin/dashboard.html - Panel administrador"
            )
            
            report_templates = System(
                name="Report Templates",
                description="reports/ventas.html, ocupacion.html - Visualizacion reportes"
            )
        
        # ===== CLIENT-SIDE LOGIC (JavaScript) =====
        with Cluster("Client-Side Logic (JavaScript)"):
            
            form_validator = System(
                name="Form Validator",
                description="Validacion HTML5 + JS en formularios"
            )
            
            seat_selector = System(
                name="Seat Selector UI",
                description="Interfaz visual seleccion asientos (complejidad adicional)"
            )
            
            ajax_handler = System(
                name="AJAX Handler",
                description="Llamadas asincronas al backend (fetch/axios)"
            )
            
            ui_interactions = System(
                name="UI Interactions",
                description="Modals, tooltips, confirmaciones, dynamic updates"
            )
            
            youtube_embed = System(
                name="YouTube Embed Handler",
                description="Integracion iframe API YouTube para trailers"
            )
        
        # ===== STYLING =====
        with Cluster("Styling Layer"):
            bootstrap_components = System(
                name="Bootstrap 5 Components",
                description="Cards, tables, forms, navs, badges, pagination"
            )
            
            custom_css = System(
                name="Custom CSS",
                description="Estilos personalizados: colores marca, layouts especificos"
            )
    
    # ===== RELACIONES =====
    
    # Usuarios -> Templates
    customer >> Relationship("Accede [HTTPS]") >> booking_templates
    customer >> Relationship("Consulta cartelera") >> movie_templates
    admin >> Relationship("Administra [HTTPS]") >> admin_templates
    admin >> Relationship("Gestiona") >> movie_templates
    
    # Templates heredan de base
    auth_templates >> Relationship("extends") >> base_template
    movie_templates >> Relationship("extends") >> base_template
    function_templates >> Relationship("extends") >> base_template
    booking_templates >> Relationship("extends") >> base_template
    admin_templates >> Relationship("extends") >> base_template
    report_templates >> Relationship("extends") >> base_template
    
    # Templates usan JavaScript components
    auth_templates >> Relationship("usa validacion") >> form_validator
    movie_templates >> Relationship("usa validacion") >> form_validator
    movie_templates >> Relationship("integra trailers") >> youtube_embed
    booking_templates >> Relationship("usa") >> seat_selector
    booking_templates >> Relationship("confirma compra") >> ui_interactions
    function_templates >> Relationship("usa") >> form_validator
    
    # JavaScript -> Backend (API calls)
    ajax_handler >> Relationship("GET/POST/PUT/DELETE\n[JSON/HTTPS]") >> backend
    seat_selector >> Relationship("consulta disponibilidad") >> ajax_handler
    form_validator >> Relationship("envia datos") >> ajax_handler
    
    # Templates -> Static Assets
    base_template >> Relationship("carga recursos") >> static_assets
    
    # Styling
    base_template >> Relationship("usa") >> bootstrap_components
    base_template >> Relationship("aplica") >> custom_css
    
    # External integration
    youtube_embed >> Relationship("embebe videos [iframe API]") >> youtube