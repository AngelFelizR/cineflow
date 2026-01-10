# models.py
# Definición de modelos ORM para el Sistema de Biblioteca

from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Autor(Base):
    """Modelo para la tabla Autores"""
    __tablename__ = 'Autores'

    AutorID = Column(Integer, primary_key=True, autoincrement=True)
    Nombre = Column(String(100), nullable=False)
    Apellido = Column(String(100), nullable=False)
    Nacionalidad = Column(String(50))
    FechaNacimiento = Column(Date)
    Biografia = Column(String(500))
    FechaRegistro = Column(DateTime, default=datetime.now)

    # Relación con Libros
    libros = relationship("Libro", back_populates="autor")

    def __repr__(self):
        return f"<Autor(id={self.AutorID}, nombre='{self.Nombre} {self.Apellido}')>"

    @property
    def nombre_completo(self):
        """Retorna el nombre completo del autor"""
        return f"{self.Nombre} {self.Apellido}"

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'AutorID': self.AutorID,
            'Nombre': self.Nombre,
            'Apellido': self.Apellido,
            'NombreCompleto': self.nombre_completo,
            'Nacionalidad': self.Nacionalidad,
            'FechaNacimiento': self.FechaNacimiento.isoformat() if self.FechaNacimiento else None,
            'Biografia': self.Biografia
        }


class Categoria(Base):
    """Modelo para la tabla Categorias"""
    __tablename__ = 'Categorias'

    CategoriaID = Column(Integer, primary_key=True, autoincrement=True)
    NombreCategoria = Column(String(100), nullable=False, unique=True)
    Descripcion = Column(String(300))

    # Relación con Libros
    libros = relationship("Libro", back_populates="categoria")

    def __repr__(self):
        return f"<Categoria(id={self.CategoriaID}, nombre='{self.NombreCategoria}')>"

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'CategoriaID': self.CategoriaID,
            'NombreCategoria': self.NombreCategoria,
            'Descripcion': self.Descripcion
        }


class Libro(Base):
    """Modelo para la tabla Libros"""
    __tablename__ = 'Libros'

    LibroID = Column(Integer, primary_key=True, autoincrement=True)
    Titulo = Column(String(200), nullable=False)
    ISBN = Column(String(20), nullable=False, unique=True)
    AutorID = Column(Integer, ForeignKey('Autores.AutorID'), nullable=False)
    CategoriaID = Column(Integer, ForeignKey('Categorias.CategoriaID'), nullable=False)
    FechaPublicacion = Column(Date)
    Editorial = Column(String(100))
    NumeroPaginas = Column(Integer)
    CopiasDisponibles = Column(Integer, default=0)
    CopiasTotal = Column(Integer, default=0)
    Descripcion = Column(String(500))
    FechaRegistro = Column(DateTime, default=datetime.now)

    # Relaciones
    autor = relationship("Autor", back_populates="libros")
    categoria = relationship("Categoria", back_populates="libros")
    prestamos = relationship("Prestamo", back_populates="libro")

    def __repr__(self):
        return f"<Libro(id={self.LibroID}, titulo='{self.Titulo}')>"

    @property
    def esta_disponible(self):
        """Verifica si hay copias disponibles"""
        return self.CopiasDisponibles > 0

    @property
    def porcentaje_disponibilidad(self):
        """Retorna el porcentaje de disponibilidad"""
        if self.CopiasTotal == 0:
            return 0
        return (self.CopiasDisponibles / self.CopiasTotal) * 100

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'LibroID': self.LibroID,
            'Titulo': self.Titulo,
            'ISBN': self.ISBN,
            'Autor': self.autor.nombre_completo if self.autor else None,
            'Categoria': self.categoria.NombreCategoria if self.categoria else None,
            'FechaPublicacion': self.FechaPublicacion.isoformat() if self.FechaPublicacion else None,
            'Editorial': self.Editorial,
            'NumeroPaginas': self.NumeroPaginas,
            'CopiasDisponibles': self.CopiasDisponibles,
            'CopiasTotal': self.CopiasTotal,
            'Descripcion': self.Descripcion,
            'EstaDisponible': self.esta_disponible
        }


class Usuario(Base):
    """Modelo para la tabla Usuarios"""
    __tablename__ = 'Usuarios'

    UsuarioID = Column(Integer, primary_key=True, autoincrement=True)
    NumeroCarnet = Column(String(20), nullable=False, unique=True)
    Nombre = Column(String(100), nullable=False)
    Apellido = Column(String(100), nullable=False)
    Email = Column(String(100), nullable=False, unique=True)
    Telefono = Column(String(20))
    Direccion = Column(String(200))
    FechaRegistro = Column(DateTime, default=datetime.now)
    Estado = Column(String(20), default='Activo')

    # Relación con Prestamos
    prestamos = relationship("Prestamo", back_populates="usuario")

    def __repr__(self):
        return f"<Usuario(id={self.UsuarioID}, carnet='{self.NumeroCarnet}')>"

    @property
    def nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.Nombre} {self.Apellido}"

    @property
    def prestamos_activos(self):
        """Retorna los préstamos activos del usuario"""
        return [p for p in self.prestamos if p.esta_activo]

    @property
    def numero_prestamos_activos(self):
        """Retorna el número de préstamos activos"""
        return len(self.prestamos_activos)

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'UsuarioID': self.UsuarioID,
            'NumeroCarnet': self.NumeroCarnet,
            'Nombre': self.Nombre,
            'Apellido': self.Apellido,
            'NombreCompleto': self.nombre_completo,
            'Email': self.Email,
            'Telefono': self.Telefono,
            'Direccion': self.Direccion,
            'Estado': self.Estado,
            'PrestamosActivos': self.numero_prestamos_activos
        }


class Prestamo(Base):
    """Modelo para la tabla Prestamos"""
    __tablename__ = 'Prestamos'

    PrestamoID = Column(Integer, primary_key=True, autoincrement=True)
    LibroID = Column(Integer, ForeignKey('Libros.LibroID'), nullable=False)
    UsuarioID = Column(Integer, ForeignKey('Usuarios.UsuarioID'), nullable=False)
    FechaPrestamo = Column(DateTime, default=datetime.now)
    FechaDevolucionEsperada = Column(Date, nullable=False)
    FechaDevolucionReal = Column(DateTime)
    Estado = Column(String(20), default='Prestado')
    Multa = Column(Numeric(10, 2), default=0)

    # Relaciones
    libro = relationship("Libro", back_populates="prestamos")
    usuario = relationship("Usuario", back_populates="prestamos")

    def __repr__(self):
        return f"<Prestamo(id={self.PrestamoID}, estado='{self.Estado}')>"

    @property
    def esta_activo(self):
        """Verifica si el préstamo está activo"""
        return self.Estado == 'Prestado' and self.FechaDevolucionReal is None

    @property
    def esta_vencido(self):
        """Verifica si el préstamo está vencido"""
        if not self.esta_activo:
            return False
        return datetime.now().date() > self.FechaDevolucionEsperada

    @property
    def dias_restantes(self):
        """Calcula los días restantes para devolver (negativo si está vencido)"""
        if not self.esta_activo:
            return 0
        delta = self.FechaDevolucionEsperada - datetime.now().date()
        return delta.days

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'PrestamoID': self.PrestamoID,
            'LibroID': self.LibroID,
            'LibroTitulo': self.libro.Titulo if self.libro else None,
            'UsuarioID': self.UsuarioID,
            'UsuarioNombre': self.usuario.nombre_completo if self.usuario else None,
            'FechaPrestamo': self.FechaPrestamo.isoformat() if self.FechaPrestamo else None,
            'FechaDevolucionEsperada': self.FechaDevolucionEsperada.isoformat() if self.FechaDevolucionEsperada else None,
            'FechaDevolucionReal': self.FechaDevolucionReal.isoformat() if self.FechaDevolucionReal else None,
            'Estado': self.Estado,
            'Multa': float(self.Multa) if self.Multa else 0,
            'EstaActivo': self.esta_activo,
            'EstaVencido': self.esta_vencido,
            'DiasRestantes': self.dias_restantes
        }


if __name__ == "__main__":
    """
    Script de prueba de los modelos
    Ejecutar: python models.py
    """
    print("=" * 80)
    print("MODELOS ORM DEFINIDOS")
    print("=" * 80)

    print("\nModelos disponibles:")
    print(f"  - {Autor.__name__}: {Autor.__doc__}")
    print(f"  - {Categoria.__name__}: {Categoria.__doc__}")
    print(f"  - {Libro.__name__}: {Libro.__doc__}")
    print(f"  - {Usuario.__name__}: {Usuario.__doc__}")
    print(f"  - {Prestamo.__name__}: {Prestamo.__doc__}")

    print("\n" + "=" * 80)
    print("Para usar estos modelos, importa desde database.py y models.py")
    print("Ejemplo:")
    print("  from database import db")
    print("  from models import Libro, Autor")
    print("  ")
    print("  session = db.get_session()")
    print("  libros = session.query(Libro).all()")
    print("=" * 80)
