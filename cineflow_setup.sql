USE CineFlow;

GO

CREATE TABLE Clasificaciones (
    Id INT IDENTITY PRIMARY KEY,
    Clasificacion VARCHAR(10) NOT NULL,
    Activo BIT DEFAULT 1
);

CREATE TABLE Generos (
    Id INT IDENTITY PRIMARY KEY,
    Genero VARCHAR(50) NOT NULL,
    Activo BIT DEFAULT 1
);

CREATE TABLE DiasSemana (
    Id INT IDENTITY PRIMARY KEY,
    DiaSemana VARCHAR(20) NOT NULL,
    DiaSemanaCorto VARCHAR(5) NOT NULL
);

CREATE TABLE RolesDeUsuario (
    Id INT IDENTITY PRIMARY KEY,
    Rol VARCHAR(50) NOT NULL
);

CREATE TABLE Peliculas (
    Id INT IDENTITY PRIMARY KEY,
    Pelicula VARCHAR(150) NOT NULL,
    IdClasificacion INT NOT NULL,
    DuracionMinutos INT NOT NULL,
    DescripcionCorta VARCHAR(255),
    DescripcionLarga VARCHAR(MAX),
    LinkToBanner VARCHAR(255),
    LinkToBajante VARCHAR(255),
    LinkToTrailer VARCHAR(255),
    Activo BIT DEFAULT 1,
    FOREIGN KEY (IdClasificacion) REFERENCES Clasificaciones(Id)
);

CREATE TABLE PeliculaGenero (
    Id INT IDENTITY PRIMARY KEY,
    IdPelicula INT NOT NULL,
    IdGenero INT NOT NULL,
    FOREIGN KEY (IdPelicula) REFERENCES Peliculas(Id),
    FOREIGN KEY (IdGenero) REFERENCES Generos(Id),
    UNIQUE (IdPelicula, IdGenero)
);
CREATE TABLE Cines (
    Id INT IDENTITY PRIMARY KEY,
    Cine VARCHAR(100) NOT NULL,
    Ubicacion VARCHAR(255),
    Telefono VARCHAR(20),
    GoogleMapIframeSrc VARCHAR(MAX),
    Activo BIT DEFAULT 1
);
CREATE TABLE TipoDeSala (
    Id INT IDENTITY PRIMARY KEY,
    Tipo VARCHAR(50) NOT NULL,
    PrecioAdulto DECIMAL(10,2) NOT NULL,
    PrecioNino DECIMAL(10,2) NOT NULL,
    Activo BIT DEFAULT 1
);
CREATE TABLE Salas (
    Id INT IDENTITY PRIMARY KEY,
    NumeroDeSala INT NOT NULL,
    IdCine INT NOT NULL,
    IdTipo INT NOT NULL,
    CantidadFilas INT NOT NULL,
    CantidadColumnas INT NOT NULL,
    Activo BIT DEFAULT 1,
    FOREIGN KEY (IdCine) REFERENCES Cines(Id),
    FOREIGN KEY (IdTipo) REFERENCES TipoDeSala(Id),
    UNIQUE (IdCine, NumeroDeSala)
);
CREATE TABLE Funciones (
    Id INT IDENTITY PRIMARY KEY,
    IdPelicula INT NOT NULL,
    IdCine INT NOT NULL,
    IdSala INT NOT NULL,
    FechaInicio DATETIME NOT NULL,
    FechaFin DATETIME NOT NULL,
    Hora TIME NOT NULL,
    IdDiaSemana INT NOT NULL,
    Estado VARCHAR(20) DEFAULT 'Programada',
    Activo BIT DEFAULT 1,
    FOREIGN KEY (IdPelicula) REFERENCES Peliculas(Id),
    FOREIGN KEY (IdCine) REFERENCES Cines(Id),
    FOREIGN KEY (IdSala) REFERENCES Salas(Id),
    FOREIGN KEY (IdDiaSemana) REFERENCES DiasSemana(Id)
);
CREATE TABLE Usuarios (
    Id INT IDENTITY PRIMARY KEY,
    IdRol INT NOT NULL,
    Nombre VARCHAR(100),
    Apellidos VARCHAR(100),
    CorreoElectronico VARCHAR(150) UNIQUE,
    Telefono VARCHAR(20),
    ContrasenaHash VARCHAR(255) NOT NULL,
    FechaNacimiento DATE,
    Activo BIT DEFAULT 1,
    FOREIGN KEY (IdRol) REFERENCES RolesDeUsuario(Id)
);

CREATE TABLE Boletos (
    Id INT IDENTITY PRIMARY KEY,
    IdFuncion INT NOT NULL,
    IdCliente INT NOT NULL,
    NumeroFila INT NOT NULL,
    NumeroColumna INT NOT NULL,
    CodigoAsiento AS (
        CONCAT(CHAR(64 + NumeroFila), NumeroColumna)
    ) PERSISTED,
    FechaCreacion DATETIME DEFAULT GETDATE(),
    Pagado BIT DEFAULT 1,
    Cancelado BIT DEFAULT 0,
    Usado BIT DEFAULT 0,
    FOREIGN KEY (IdFuncion) REFERENCES Funciones(Id),
    UNIQUE (IdFuncion, NumeroFila, NumeroColumna)
);

CREATE TABLE MontosCancelados (
    Id INT IDENTITY PRIMARY KEY,
    IdBoleto INT NOT NULL,
    IdUsuario INT NOT NULL,
    FechaCancelacion DATETIME DEFAULT GETDATE(),
    MontoCancelado DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (IdBoleto) REFERENCES Boletos(Id),
    FOREIGN KEY (IdUsuario) REFERENCES Usuarios(Id)
);

