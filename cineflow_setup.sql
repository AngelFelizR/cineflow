-- # Ingresar a Base de Datos

USE CineFlow;

GO

-- # Crear tablas

CREATE TABLE Clasificaciones (
    Id INT IDENTITY PRIMARY KEY,
    Clasificación NVARCHAR(10) NOT NULL UNIQUE,
    Activo BIT DEFAULT 1
);

CREATE TABLE Idiomas (
    Id INT IDENTITY PRIMARY KEY,
    Idioma NVARCHAR(10) NOT NULL UNIQUE,
    Activo BIT DEFAULT 1
);

CREATE TABLE Géneros (
    Id INT IDENTITY PRIMARY KEY,
    Género NVARCHAR(50) NOT NULL UNIQUE,
    Activo BIT DEFAULT 1
);

CREATE TABLE Cines (
    Id INT IDENTITY PRIMARY KEY,
    Cine NVARCHAR(100) NOT NULL UNIQUE,
    Dirección NVARCHAR(255) NOT NULL UNIQUE,
    Teléfono NVARCHAR(20) NOT NULL UNIQUE,
    GoogleMapIframeSrc   NVARCHAR(MAX) NOT NULL,
    Activo BIT DEFAULT 1
);

CREATE TABLE TipoDeSala (
    Id INT IDENTITY PRIMARY KEY,
    Tipo NVARCHAR(50) NOT NULL UNIQUE,
    PrecioAdulto DECIMAL(10,4) NOT NULL,
    PrecioNino DECIMAL(10,4) NOT NULL,
    Activo BIT DEFAULT 1
);

CREATE TABLE RolesDeUsuario (
    Id INT IDENTITY PRIMARY KEY,
    Rol NVARCHAR(50) NOT NULL UNIQUE,
    Activo BIT DEFAULT 1
);

CREATE TABLE TipoBoletos (
    Id INT IDENTITY PRIMARY KEY,
    TipoBoleto NVARCHAR(50) NOT NULL UNIQUE,
    Activo BIT DEFAULT 1
);

CREATE TABLE Películas (
    Id INT IDENTITY PRIMARY KEY,
    IdClasificación INT NOT NULL,
    IdIdioma INT NOT NULL,
    TítuloPelícula NVARCHAR(150) NOT NULL,
    DuraciónMinutos INT NOT NULL,
    DescripciónCorta NVARCHAR(255) NOT NULL,
    DescripciónLarga NVARCHAR(MAX) NOT NULL,
    LinkToBanner NVARCHAR(MAX) NOT NULL,
    LinkToBajante NVARCHAR(MAX) NOT NULL,
    LinkToTrailer NVARCHAR(MAX) NOT NULL,
    Activo BIT DEFAULT 1,
    FOREIGN KEY (IdClasificación) REFERENCES Clasificaciones(Id),
    FOREIGN KEY (IdIdioma) REFERENCES Idiomas(Id)
);

CREATE TABLE PeliculaGenero (
    Id INT IDENTITY PRIMARY KEY,
    IdPelícula INT NOT NULL,
    IdGénero INT NOT NULL,
    FOREIGN KEY (IdPelícula) REFERENCES Películas(Id),
    FOREIGN KEY (IdGénero) REFERENCES Géneros(Id),
    UNIQUE (IdPelícula, IdGénero)
);


CREATE TABLE Salas (
    Id INT IDENTITY PRIMARY KEY,
    IdCine INT NOT NULL,
    IdTipo INT NOT NULL,
    NúmeroDeSala INT NOT NULL,
    Activo BIT DEFAULT 1,
    FOREIGN KEY (IdCine) REFERENCES Cines(Id),
    FOREIGN KEY (IdTipo) REFERENCES TipoDeSala(Id),
    UNIQUE (IdCine, NúmeroDeSala)
);

CREATE TABLE Asientos (
    Id INT IDENTITY PRIMARY KEY,
    IdSala INT NOT NULL,
    CódigoAsiento NVARCHAR(3) NOT NULL,
    Activo BIT DEFAULT 1,
    FOREIGN KEY (IdSala) REFERENCES Salas(Id),
    UNIQUE (IdSala, CódigoAsiento)
);


CREATE TABLE Funciones (
    Id INT IDENTITY PRIMARY KEY,
    IdPelícula INT NOT NULL,
    IdSala INT NOT NULL,
    FechaHora DATETIME2 NOT NULL,
    Activo BIT DEFAULT 1,
    FOREIGN KEY (IdPelícula) REFERENCES Películas(Id),
    FOREIGN KEY (IdSala) REFERENCES Salas(Id)
);

CREATE TABLE Usuarios (
    Id INT IDENTITY PRIMARY KEY,
    IdRol INT NOT NULL,
    Nombre NVARCHAR(100) NOT NULL,
    Apellidos NVARCHAR(100) NOT NULL,
    CorreoElectrónico NVARCHAR(150) NOT NULL UNIQUE,
    Teléfono NVARCHAR(20),
    ContraseñaHash NVARCHAR(MAX) NOT NULL,
    FechaNacimiento DATE,
    FOREIGN KEY (IdRol) REFERENCES RolesDeUsuario(Id)
);

CREATE TABLE Boletos (
    Id INT IDENTITY PRIMARY KEY,
    IdFunción INT NOT NULL,
    IdAsiento INT NOT NULL,
    IdUsuario INT NOT NULL,
    IdTipoBoleto INT NOT NULL,
    FechaCreacion DATETIME2 DEFAULT GETDATE(),
    ValorPagado DECIMAL(10, 4) NOT NULL,
    FOREIGN KEY (IdFunción) REFERENCES Funciones(Id),
    FOREIGN KEY (IdAsiento) REFERENCES Asientos(Id),
    FOREIGN KEY (IdUsuario) REFERENCES Usuarios(Id),
    FOREIGN KEY (IdTipoBoleto) REFERENCES TipoBoletos(Id),
    UNIQUE (IdFunción, IdAsiento)
);

CREATE TABLE BoletosCancelados (
    Id INT IDENTITY PRIMARY KEY,
    IdBoleto INT NOT NULL UNIQUE,
    FechaCancelacion DATETIME2 DEFAULT GETDATE(),
    ValorAcreditado DECIMAL(10,4) NOT NULL,
    Canjeado BIT DEFAULT 0,
    FOREIGN KEY (IdBoleto) REFERENCES Boletos(Id)
);

CREATE TABLE BoletosUsados(
    Id INT IDENTITY PRIMARY KEY,
    IdBoleto INT NOT NULL UNIQUE,
    IdEncargado INT NOT NULL,
    FechaUso DATETIME2 DEFAULT GETDATE()
    FOREIGN KEY (IdBoleto) REFERENCES Boletos(Id),
    FOREIGN KEY (IdEncargado) REFERENCES Usuarios(Id)
);

GO

-- # Crear validaciones

CREATE TRIGGER trg_ValidarTiempoFunciones
ON Funciones
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    IF EXISTS (
        -- Verificar conflictos entre funciones en la misma sala
        SELECT 1
        FROM inserted i
        INNER JOIN Películas p ON i.IdPelícula = p.Id
        INNER JOIN Funciones f ON i.IdSala = f.IdSala 
            AND f.Id != i.Id -- Excluir la misma función
        INNER JOIN Películas pf ON f.IdPelícula = pf.Id
        WHERE 
            -- Condición 1: Nueva función empieza durante otra función + intervalo
            (i.FechaHora >= f.FechaHora 
             AND i.FechaHora < DATEADD(MINUTE, pf.DuraciónMinutos + 25, f.FechaHora))
            OR
            -- Condición 2: Otra función empieza durante nueva función + intervalo
            (f.FechaHora >= i.FechaHora 
             AND f.FechaHora < DATEADD(MINUTE, p.DuraciónMinutos + 25, i.FechaHora))
    )
    BEGIN
        THROW 50000, 'Violación del tiempo mínimo entre funciones (Duración + 25 minutos)', 1;
        ROLLBACK TRANSACTION;
    END
END;


-- # Ingresar Datos


-- # Create vistas a usar

CREATE VIEW vw_PelículasPopulares AS
SELECT TOP 3
    p.Id, p.TítuloPelícula, p.DescripciónCorta, p.LinkToBanner,
    p.DuraciónMinutos, i.Idioma, c.Clasificación,
    COUNT(b.Id) as TotalBoletos
FROM Películas p
JOIN Idiomas i ON p.IdIdioma = i.Id
JOIN Clasificaciones c ON p.IdClasificación = c.Id
LEFT JOIN Funciones f ON p.Id = f.IdPelícula
LEFT JOIN Boletos b ON f.Id = b.IdFunción
WHERE p.Activo = 1
GROUP BY p.Id, p.TítuloPelícula, p.DescripciónCorta, p.LinkToBanner, p.DuraciónMinutos, i.Idioma, c.Clasificación
ORDER BY TotalBoletos DESC;
