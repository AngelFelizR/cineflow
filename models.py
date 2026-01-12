# models.py
from database import db
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    String, Integer, Boolean, Date, DateTime,
    ForeignKey, Numeric
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

from flask_login import UserMixin, LoginManager
from flask_bcrypt import Bcrypt

login_manager = LoginManager()
bcrypt = Bcrypt()


# =========================
# Catálogos
# =========================

class Clasificacion(Base):
    __tablename__ = "Clasificaciones"

    Id: Mapped[int] = mapped_column(primary_key=True)
    Clasificacion: Mapped[str] = mapped_column(
        "Clasificación", String(10), unique=True, nullable=False
    )
    Activo: Mapped[bool] = mapped_column(Boolean, default=True)

    peliculas: Mapped[List["Pelicula"]] = relationship(back_populates="clasificacion")


class Idioma(Base):
    __tablename__ = "Idiomas"

    Id: Mapped[int] = mapped_column(primary_key=True)
    Idioma: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    Activo: Mapped[bool] = mapped_column(Boolean, default=True)

    peliculas: Mapped[List["Pelicula"]] = relationship(back_populates="idioma")


class Genero(Base):
    __tablename__ = "Géneros"

    Id: Mapped[int] = mapped_column(primary_key=True)
    Genero: Mapped[str] = mapped_column(
        "Género", String(50), unique=True, nullable=False
    )
    Activo: Mapped[bool] = mapped_column(Boolean, default=True)

    peliculas: Mapped[List["PeliculaGenero"]] = relationship(back_populates="genero")


class RolUsuario(Base):
    __tablename__ = "RolesDeUsuario"

    Id: Mapped[int] = mapped_column(primary_key=True)
    Rol: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    Activo: Mapped[bool] = mapped_column(Boolean, default=True)

    usuarios: Mapped[List["Usuario"]] = relationship(back_populates="rol")


class TipoBoleto(Base):
    __tablename__ = "TipoBoletos"

    Id: Mapped[int] = mapped_column(primary_key=True)
    TipoBoleto: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    Activo: Mapped[bool] = mapped_column(Boolean, default=True)

    boletos: Mapped[List["Boleto"]] = relationship(back_populates="tipo_boleto")


# =========================
# Cines y Salas
# =========================

class Cine(Base):
    __tablename__ = "Cines"

    Id: Mapped[int] = mapped_column(primary_key=True)
    Cine: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    Direccion: Mapped[str] = mapped_column(
        "Dirección", String(255), unique=True, nullable=False
    )
    Telefono: Mapped[str] = mapped_column(
        "Teléfono", String(20), unique=True, nullable=False
    )
    GoogleMapIframeSrc: Mapped[str] = mapped_column(String, nullable=False)
    Activo: Mapped[bool] = mapped_column(Boolean, default=True)

    salas: Mapped[List["Sala"]] = relationship(back_populates="cine")


class TipoSala(Base):
    __tablename__ = "TipoDeSala"

    Id: Mapped[int] = mapped_column(primary_key=True)
    Tipo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    PrecioAdulto: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    PrecioNino: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    Activo: Mapped[bool] = mapped_column(Boolean, default=True)

    salas: Mapped[List["Sala"]] = relationship(back_populates="tipo_sala")


class Sala(Base):
    __tablename__ = "Salas"

    Id: Mapped[int] = mapped_column(primary_key=True)
    IdCine: Mapped[int] = mapped_column(ForeignKey("Cines.Id"), nullable=False)
    IdTipo: Mapped[int] = mapped_column(ForeignKey("TipoDeSala.Id"), nullable=False)

    NumeroDeSala: Mapped[int] = mapped_column(
        "NúmeroDeSala", Integer, nullable=False
    )
    Activo: Mapped[bool] = mapped_column(Boolean, default=True)

    cine: Mapped["Cine"] = relationship(back_populates="salas")
    tipo_sala: Mapped["TipoSala"] = relationship(back_populates="salas")
    asientos: Mapped[List["Asiento"]] = relationship(back_populates="sala")
    funciones: Mapped[List["Funcion"]] = relationship(back_populates="sala")


class Asiento(Base):
    __tablename__ = "Asientos"

    Id: Mapped[int] = mapped_column(primary_key=True)
    IdSala: Mapped[int] = mapped_column(ForeignKey("Salas.Id"), nullable=False)
    CodigoAsiento: Mapped[str] = mapped_column(
        "CódigoAsiento", String(3), nullable=False
    )
    Activo: Mapped[bool] = mapped_column(Boolean, default=True)

    sala: Mapped["Sala"] = relationship(back_populates="asientos")
    boletos: Mapped[List["Boleto"]] = relationship(back_populates="asiento")


# =========================
# Películas
# =========================

class Pelicula(Base):
    __tablename__ = "Películas"

    Id: Mapped[int] = mapped_column(primary_key=True)
    IdClasificacion: Mapped[int] = mapped_column(
        "IdClasificación", ForeignKey("Clasificaciones.Id"), nullable=False
    )
    IdIdioma: Mapped[int] = mapped_column(
        ForeignKey("Idiomas.Id"), nullable=False
    )

    Titulo: Mapped[str] = mapped_column(
        "TítuloPelícula", String(150), nullable=False
    )
    DuracionMinutos: Mapped[int] = mapped_column(
        "DuraciónMinutos", Integer, nullable=False
    )
    DescripcionCorta: Mapped[str] = mapped_column(
        "DescripciónCorta", String(255), nullable=False
    )
    DescripcionLarga: Mapped[str] = mapped_column(
        "DescripciónLarga", String, nullable=False
    )
    LinkToBanner: Mapped[str] = mapped_column(String, nullable=False)
    LinkToBajante: Mapped[str] = mapped_column(String, nullable=False)
    LinkToTrailer: Mapped[str] = mapped_column(String, nullable=False)
    Activo: Mapped[bool] = mapped_column(Boolean, default=True)

    clasificacion: Mapped["Clasificacion"] = relationship(back_populates="peliculas")
    idioma: Mapped["Idioma"] = relationship(back_populates="peliculas")
    generos: Mapped[List["PeliculaGenero"]] = relationship(back_populates="pelicula")
    funciones: Mapped[List["Funcion"]] = relationship(back_populates="pelicula")


class PeliculaGenero(Base):
    __tablename__ = "PeliculaGenero"

    Id: Mapped[int] = mapped_column(primary_key=True)
    IdPelicula: Mapped[int] = mapped_column(
        "IdPelícula", ForeignKey("Películas.Id"), nullable=False
    )
    IdGenero: Mapped[int] = mapped_column(
        "IdGénero", ForeignKey("Géneros.Id"), nullable=False
    )

    pelicula: Mapped["Pelicula"] = relationship(back_populates="generos")
    genero: Mapped["Genero"] = relationship(back_populates="peliculas")


# =========================
# Funciones y Boletos
# =========================

class Funcion(Base):
    __tablename__ = "Funciones"

    Id: Mapped[int] = mapped_column(primary_key=True)
    IdPelicula: Mapped[int] = mapped_column(
        "IdPelícula", ForeignKey("Películas.Id"), nullable=False
    )
    IdSala: Mapped[int] = mapped_column(
        ForeignKey("Salas.Id"), nullable=False
    )
    FechaHora: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    Activo: Mapped[bool] = mapped_column(Boolean, default=True)

    pelicula: Mapped["Pelicula"] = relationship(back_populates="funciones")
    sala: Mapped["Sala"] = relationship(back_populates="funciones")
    boletos: Mapped[List["Boleto"]] = relationship(back_populates="funcion")


class Usuario(Base, UserMixin):
    __tablename__ = "Usuarios"

    Id: Mapped[int] = mapped_column(primary_key=True)
    IdRol: Mapped[int] = mapped_column(ForeignKey("RolesDeUsuario.Id"), nullable=False)
    Nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    Apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    CorreoElectronico: Mapped[str] = mapped_column(
        "CorreoElectrónico", String(150), unique=True, nullable=False
    )
    Telefono: Mapped[Optional[str]] = mapped_column("Teléfono", String(20))
    ContrasenaHash: Mapped[str] = mapped_column("ContraseñaHash", String, nullable=False)
    FechaNacimiento: Mapped[Optional[date]] = mapped_column(Date)

    def __repr__(self):
        return '<User Name {}>'.format(self.Nombre + self.Apellidos)

    def guardar_contrasena(self, contrasena):
        self.ContrasenaHash = bcrypt.generate_password_hash(contrasena).decode()

    def validar_contrasena(self, contrasena):
        return bcrypt.check_password_hash(self.ContrasenaHash, contrasena)

    rol: Mapped["RolUsuario"] = relationship(back_populates="usuarios")
    boletos: Mapped[List["Boleto"]] = relationship(back_populates="usuario")


class Boleto(Base):
    __tablename__ = "Boletos"

    Id: Mapped[int] = mapped_column(primary_key=True)
    IdFuncion: Mapped[int] = mapped_column(
        "IdFunción", ForeignKey("Funciones.Id"), nullable=False
    )
    IdAsiento: Mapped[int] = mapped_column(ForeignKey("Asientos.Id"), nullable=False)
    IdUsuario: Mapped[int] = mapped_column(ForeignKey("Usuarios.Id"), nullable=False)
    IdTipoBoleto: Mapped[int] = mapped_column(
        ForeignKey("TipoBoletos.Id"), nullable=False
    )

    FechaCreacion: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    ValorPagado: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)

    funcion: Mapped["Funcion"] = relationship(back_populates="boletos")
    asiento: Mapped["Asiento"] = relationship(back_populates="boletos")
    usuario: Mapped["Usuario"] = relationship(back_populates="boletos")
    tipo_boleto: Mapped["TipoBoleto"] = relationship(back_populates="boletos")


class BoletoCancelado(Base):
    __tablename__ = "BoletosCancelados"

    Id: Mapped[int] = mapped_column(primary_key=True)
    IdBoleto: Mapped[int] = mapped_column(
        ForeignKey("Boletos.Id"), unique=True, nullable=False
    )
    FechaCancelacion: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    ValorAcreditado: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    Canjeado: Mapped[bool] = mapped_column(Boolean, default=False)


class BoletoUsado(Base):
    __tablename__ = "BoletosUsados"

    Id: Mapped[int] = mapped_column(primary_key=True)
    IdBoleto: Mapped[int] = mapped_column(
        ForeignKey("Boletos.Id"), unique=True, nullable=False
    )
    IdEncargado: Mapped[int] = mapped_column(
        ForeignKey("Usuarios.Id"), nullable=False
    )
    FechaUso: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


@login_manager.user_loader
def load_user(user_id):
    # Usamos la sesión de tu clase Database
    session = db.get_session()
    try:
        # Buscamos al usuario por su ID (clave primaria)
        return session.get(Usuario, int(user_id))
    finally:
        session.close()