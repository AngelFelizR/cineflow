from diagrams import Diagram
from diagrams.c4 import Person, System, Relationship

graph_attr = {
    "splines": "spline",
}

with Diagram("01 - Sistema de Gestión de Cine", direction="TB", graph_attr=graph_attr):
    
    customer = Person(
        name="Cliente",
        description="Persona que accede al sistema para consultar funciones y comprar entradas."
    )
    
    admin = Person(
        name="Administrador",
        description="Usuario responsable de la gestión de películas, funciones y cartelera."
    )
   
    webapp = System(
        name="Sistema Web de Cine",
        description="Aplicación web que permite: Venta de entradas y Administración del cine"
    )

    youtube = System(
        name="YouTube",
        description="Plataforma externa para reproducir trailers de películas",
        external=True
    )

    customer >> Relationship("Accede mediante HTTPS") >> webapp
    admin >> Relationship("Administra el sistema mediante HTTPS") >> webapp
    webapp >> Relationship("Embebe/Reproduce trailers mediante API") >> youtube