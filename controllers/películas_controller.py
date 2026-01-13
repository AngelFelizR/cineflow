# controllers/libro_controller.py
# Controlador para operaciones de libros

from models import Pelicula
from database import db
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

class LibroController:
    """Controlador para operaciones de libros"""

    def __init__(self):
        pass  # No mantener sesión persistente

    def obtener_todos(self):
        """
        Obtiene todos los libros

        Returns:
            list: Lista de objetos Libro
        """
        session = db.get_session()
        try:
            libros = session.query(Libro).options(
                joinedload(Libro.autor),
                joinedload(Libro.categoria),
                joinedload(Libro.prestamos)
            ).all()
            # Expunge objetos para usarlos fuera de la sesión
            for libro in libros:
                session.expunge(libro)
            return libros
        except Exception as e:
            print(f"Error al obtener libros: {e}")
            return []
        finally:
            session.close()

    def obtener_por_id(self, libro_id):
        """
        Obtiene un libro por su ID

        Args:
            libro_id (int): ID del libro

        Returns:
            Libro: Objeto Libro o None
        """
        session = db.get_session()
        try:
            libro = session.query(Libro).options(
                joinedload(Libro.autor),
                joinedload(Libro.categoria)
            ).filter(Libro.LibroID == libro_id).first()
            if libro:
                session.expunge(libro)
            return libro
        except Exception as e:
            print(f"Error al obtener libro: {e}")
            return None
        finally:
            session.close()

    def buscar(self, termino_busqueda):
        """
        Busca libros por título, autor o ISBN

        Args:
            termino_busqueda (str): Término de búsqueda

        Returns:
            list: Lista de libros encontrados
        """
        session = db.get_session()
        try:
            libros = session.query(Libro).join(Autor).options(
                joinedload(Libro.autor),
                joinedload(Libro.categoria)
            ).filter(
                or_(
                    Libro.Titulo.like(f'%{termino_busqueda}%'),
                    Libro.ISBN.like(f'%{termino_busqueda}%'),
                    Autor.Nombre.like(f'%{termino_busqueda}%'),
                    Autor.Apellido.like(f'%{termino_busqueda}%')
                )
            ).all()

            for libro in libros:
                session.expunge(libro)
            return libros
        except Exception as e:
            print(f"Error en la búsqueda: {e}")
            return []
        finally:
            session.close()

    def crear(self, datos_libro):
        """
        Crea un nuevo libro

        Args:
            datos_libro (dict): Diccionario con los datos del libro

        Returns:
            tuple: (éxito: bool, mensaje: str, libro_id: int)
        """
        session = db.get_session()
        try:
            # Verificar que el autor existe
            autor = session.query(Autor).filter(
                Autor.AutorID == datos_libro['autor_id']
            ).first()

            if not autor:
                return (False, "El autor especificado no existe", None)

            # Verificar que la categoría existe
            categoria = session.query(Categoria).filter(
                Categoria.CategoriaID == datos_libro['categoria_id']
            ).first()

            if not categoria:
                return (False, "La categoría especificada no existe", None)

            # Crear el nuevo libro
            nuevo_libro = Libro(
                Titulo=datos_libro['titulo'],
                ISBN=datos_libro['isbn'],
                AutorID=datos_libro['autor_id'],
                CategoriaID=datos_libro['categoria_id'],
                Editorial=datos_libro.get('editorial'),
                NumeroPaginas=datos_libro.get('numero_paginas'),
                CopiasDisponibles=datos_libro.get('copias', 0),
                CopiasTotal=datos_libro.get('copias', 0),
                Descripcion=datos_libro.get('descripcion')
            )

            session.add(nuevo_libro)
            session.commit()

            libro_id = nuevo_libro.LibroID

            return (True, f"Libro '{nuevo_libro.Titulo}' creado exitosamente", libro_id)

        except Exception as e:
            session.rollback()
            return (False, f"Error al crear libro: {e}", None)
        finally:
            session.close()

    def actualizar(self, libro_id, datos_actualizados):
        """
        Actualiza un libro existente

        Args:
            libro_id (int): ID del libro a actualizar
            datos_actualizados (dict): Datos a actualizar

        Returns:
            tuple: (éxito: bool, mensaje: str)
        """
        session = db.get_session()
        try:
            libro = session.query(Libro).filter(Libro.LibroID == libro_id).first()

            if not libro:
                return (False, f"No se encontró el libro con ID {libro_id}")

            # Actualizar campos
            for campo, valor in datos_actualizados.items():
                if hasattr(libro, campo):
                    setattr(libro, campo, valor)

            session.commit()

            return (True, f"Libro '{libro.Titulo}' actualizado exitosamente")

        except Exception as e:
            session.rollback()
            return (False, f"Error al actualizar libro: {e}")
        finally:
            session.close()

    def eliminar(self, libro_id):
        """
        Elimina un libro

        Args:
            libro_id (int): ID del libro a eliminar

        Returns:
            tuple: (éxito: bool, mensaje: str)
        """
        session = db.get_session()
        try:
            libro = session.query(Libro).filter(Libro.LibroID == libro_id).first()

            if not libro:
                return (False, f"No se encontró el libro con ID {libro_id}")

            # Verificar si tiene préstamos activos
            if libro.prestamos:
                prestamos_activos = [p for p in libro.prestamos if p.esta_activo]
                if prestamos_activos:
                    return (False, "No se puede eliminar: el libro tiene préstamos activos")

            titulo = libro.Titulo
            session.delete(libro)
            session.commit()

            return (True, f"Libro '{titulo}' eliminado exitosamente")

        except Exception as e:
            session.rollback()
            return (False, f"Error al eliminar libro: {e}")
        finally:
            session.close()

    def obtener_disponibles(self):
        """
        Obtiene todos los libros con copias disponibles

        Returns:
            list: Lista de libros disponibles
        """
        session = db.get_session()
        try:
            libros = session.query(Libro).options(
                joinedload(Libro.autor),
                joinedload(Libro.categoria)
            ).filter(Libro.CopiasDisponibles > 0).all()

            for libro in libros:
                session.expunge(libro)
            return libros
        except Exception as e:
            print(f"Error al obtener libros disponibles: {e}")
            return []
        finally:
            session.close()
