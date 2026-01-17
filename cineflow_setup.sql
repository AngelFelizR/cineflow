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
    PrecioNiño DECIMAL(10,4) NOT NULL,
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
    FOREIGN KEY (IdRol) REFERENCES RolesDeUsuario(Id),
    UNIQUE (CorreoElectrónico),
    UNIQUE (Teléfono)
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

GO

-- # Ingresar Datos

INSERT INTO Clasificaciones (Clasificación) VALUES
('N/S'),
('NR'),
('R/14'),
('R/16'),
('R/18');

INSERT INTO Géneros (Género) VALUES
('Acción'),
('Comedia'),
('Drama'),
('Animación'),
('Terror'),
('Ciencia Ficción'),
('Aventura');

INSERT INTO RolesDeUsuario (Rol) VALUES
('Administrador'),
('Encargado de Entrada'),
('Cliente');

INSERT INTO TipoDeSala (Tipo, PrecioAdulto, PrecioNiño) VALUES
('2D', 350.00, 200.00),
('3D', 450.00, 250.00),
('CxC', 600.00, 350.00);

INSERT INTO Cines (Cine, Dirección, Teléfono, GoogleMapIframeSrc)
VALUES (
    'Caribbean Cinemas Megacentro',
    'Megacentro, Santo Domingo Este',
    '809-544-2622',
    'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d288.0811221625557!2d-69.85722296657518!3d18.506539050388852!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8eaf86298704b5c9%3A0x9311b9d6fbdff46!2sCaribbean%20Cinemas%20Megaplex%2010!5e0!3m2!1ses-419!2sdo!4v1768609435800!5m2!1ses-419!2sdo'
);


-- Inserts generados para la tabla Usuarios
INSERT INTO Usuarios (IdRol, Nombre, Apellidos, CorreoElectrónico, Teléfono, ContraseñaHash, FechaNacimiento) VALUES
(1, 'Admin', 'CineFlow', 'admin@cineflow.com', '809-555-0001', '$2b$12$mdWsWi5RQ9QOo7kB1s/aOOWY6wLiV2uyPhHgy/bC91Q69ogQ/jpby', '1985-01-01'),
(2, 'Encargado', 'Entrada', 'encargado_entrada@cineflow.com', '809-555-0002', '$2b$12$VIyGj7KskR3di7yFsM.KNe2jjrouEJBJ/yeE9ISkQbX7B8S1bw3eS', '1990-02-02'),
(3, 'Cliente1', 'Apellido', 'usuario_1@example.com', '809-000-0001', '$2b$12$w6K4GpfoowV2y8p3C9tF0.M1hx9W9AzXXfjygxU4tvCch.Ce.X13e', '1995-01-01'),
(3, 'Cliente2', 'Apellido', 'usuario_2@example.com', '809-000-0002', '$2b$12$xjteXvdvU5HFV7fG04GmnuZQWkTh9/cXvJprRuwQ7F4zZDUvy6HnK', '1995-01-01'),
(3, 'Cliente3', 'Apellido', 'usuario_3@example.com', '809-000-0003', '$2b$12$8jDHZ8Mt2iwk.E9KeCy6JO3VtLzxYZ0xv/h4fckldHg2UsEzkcft.', '1995-01-01'),
(3, 'Cliente4', 'Apellido', 'usuario_4@example.com', '809-000-0004', '$2b$12$HaKVob8InD0zVq2E2kYCXeFzpYX6KoJJEDCypyuEiUJ29LX6.d4d6', '1995-01-01'),
(3, 'Cliente5', 'Apellido', 'usuario_5@example.com', '809-000-0005', '$2b$12$Pnbbo.fq5phFFplUiq7a8uNWFXQU6UFaGHYfuFurW71cwnhkC.iwO', '1995-01-01'),
(3, 'Cliente6', 'Apellido', 'usuario_6@example.com', '809-000-0006', '$2b$12$7N7dJckHR7SorLLU95NIWOSv4JAnNHaVKTpw86LRtEdiydKMp1J7S', '1995-01-01'),
(3, 'Cliente7', 'Apellido', 'usuario_7@example.com', '809-000-0007', '$2b$12$Q5zFgXW95hhB2GBBiOh3oeSFURNEsOVNLzVg31ueahjBOK6Z/j34C', '1995-01-01'),
(3, 'Cliente8', 'Apellido', 'usuario_8@example.com', '809-000-0008', '$2b$12$Mi5yhGcwZbiVxweKcwRps.v1lFzgNpfMMYPhREVO7bjC2pwb9d9Ru', '1995-01-01'),
(3, 'Cliente9', 'Apellido', 'usuario_9@example.com', '809-000-0009', '$2b$12$hI8xl5GGhV0aqnyLk64pluRRz1VNPiVEVi18gioLxyfMvdNrCjCYq', '1995-01-01'),
(3, 'Cliente10', 'Apellido', 'usuario_10@example.com', '809-000-0010', '$2b$12$9SNUltQ6A2SCbv2j03omCuDld42v/JOw.XPlnxubGlM6C3QEijPyS', '1995-01-01'),
(3, 'Cliente11', 'Apellido', 'usuario_11@example.com', '809-000-0011', '$2b$12$5kR.l6Z.TDDv/MSzRKP.YeDsfXCSL60E2XPKDdN2Iko/Cj0t4t7Hm', '1995-01-01'),
(3, 'Cliente12', 'Apellido', 'usuario_12@example.com', '809-000-0012', '$2b$12$JdtCip5tnfB8ofYuRA.I6OkT9XvG7Hn1m0eBRqxGpvw9PxH5O6OiO', '1995-01-01'),
(3, 'Cliente13', 'Apellido', 'usuario_13@example.com', '809-000-0013', '$2b$12$M.flyj7SaWTDPTaJLlhhSeNpkLWsyCJuVRTD4hOIngqi1XNh19Ale', '1995-01-01'),
(3, 'Cliente14', 'Apellido', 'usuario_14@example.com', '809-000-0014', '$2b$12$qGiB4pcAAUjjBY35//wcg.MriTRBcud9oY1GRsY4NSzJslBGu3N26', '1995-01-01'),
(3, 'Cliente15', 'Apellido', 'usuario_15@example.com', '809-000-0015', '$2b$12$DdWtr3hYD5NRZYVjSO4KmOzCkWGPL6QVNkkH9gfFlbIbQbvLdJbJi', '1995-01-01'),
(3, 'Cliente16', 'Apellido', 'usuario_16@example.com', '809-000-0016', '$2b$12$.PEaHf3fc8QSvP6fElzK2OGoeG.bTgy8RpJK62lckTrSJ7sFQmU1O', '1995-01-01'),
(3, 'Cliente17', 'Apellido', 'usuario_17@example.com', '809-000-0017', '$2b$12$QBi29zg/gRKUlbDo0K0le.5iocjDt0mXwYqUkvpbswaKvJDiJFOFO', '1995-01-01'),
(3, 'Cliente18', 'Apellido', 'usuario_18@example.com', '809-000-0018', '$2b$12$HGZF9olYRb6FGKYTsXcRfuP2Yrku77qnMDhcPsIqWcN/tNgNUidFG', '1995-01-01'),
(3, 'Cliente19', 'Apellido', 'usuario_19@example.com', '809-000-0019', '$2b$12$eq07Qp7o6rP2U0NxTRWkruEJRvFrdR37PBxil1CK6zAuJo/ji6pkO', '1995-01-01'),
(3, 'Cliente20', 'Apellido', 'usuario_20@example.com', '809-000-0020', '$2b$12$H7sL1OA.3mx4a8Txw5vZv.Jee7vS8i6pXnVQ5ijLjWB9OGVAb8Fri', '1995-01-01'),
(3, 'Cliente21', 'Apellido', 'usuario_21@example.com', '809-000-0021', '$2b$12$InkHUtToXqrHqAgkuorT/u3oacIxS8xUh8VxeRrlFx7tJTlY9SFIe', '1995-01-01'),
(3, 'Cliente22', 'Apellido', 'usuario_22@example.com', '809-000-0022', '$2b$12$4qMAS2e2u/4tCUT9iN2FEuvqO1Xl3BMx0Se4hjccpZWnJiWKE3lCq', '1995-01-01'),
(3, 'Cliente23', 'Apellido', 'usuario_23@example.com', '809-000-0023', '$2b$12$DMX08BVmQ2UUU5RtkGbsje/Qb7.YsgDsnKd6SJtnj07cakuxnwo5C', '1995-01-01'),
(3, 'Cliente24', 'Apellido', 'usuario_24@example.com', '809-000-0024', '$2b$12$SLW6UKN3s1Hzk2dvg2ZuCemLz54hljyFhZ/RkrAuSb0SG6EEULAaG', '1995-01-01'),
(3, 'Cliente25', 'Apellido', 'usuario_25@example.com', '809-000-0025', '$2b$12$vhXSo6KUTmWheH1fd5EAxeelaN2XKMUQXq7EDCZ3VAAsDX3DS4AY.', '1995-01-01'),
(3, 'Cliente26', 'Apellido', 'usuario_26@example.com', '809-000-0026', '$2b$12$Q2tKD/fxSCk4yAihP/r37.2UfWF7y3vgTADHE9dO5w3vFQkKXx6s2', '1995-01-01'),
(3, 'Cliente27', 'Apellido', 'usuario_27@example.com', '809-000-0027', '$2b$12$7dxr.xNhIAlM85yInjEJe.qceDLa3qx/xXNEn0TbhTrYggnaNTs4W', '1995-01-01'),
(3, 'Cliente28', 'Apellido', 'usuario_28@example.com', '809-000-0028', '$2b$12$lL2HBgfLZ4qlPsUQUBTrY.xUeUF9EdjnrTlF/pQv4BdeSx4a/uevq', '1995-01-01'),
(3, 'Cliente29', 'Apellido', 'usuario_29@example.com', '809-000-0029', '$2b$12$YEGQGuTwfwWAmDBEBpnzg.Il4F4kTW362cd43UOlZrsxd7ASm4/py', '1995-01-01'),
(3, 'Cliente30', 'Apellido', 'usuario_30@example.com', '809-000-0030', '$2b$12$MR1d/5PZQDG5osaSOFVxceFqOIpRjXhvLWOnJuA77j7EpOV.EkzZy', '1995-01-01'),
(3, 'Cliente31', 'Apellido', 'usuario_31@example.com', '809-000-0031', '$2b$12$eMqasE1K6XqQMDdiNvZQ..F/5Hj6CcMfFJXo1HFJOL.c75l/QFh7i', '1995-01-01'),
(3, 'Cliente32', 'Apellido', 'usuario_32@example.com', '809-000-0032', '$2b$12$9uvxe/FuWw7ygyonBfMfA.v2NmIvqDM3MkTK95/5/ATcWNXWKM2km', '1995-01-01'),
(3, 'Cliente33', 'Apellido', 'usuario_33@example.com', '809-000-0033', '$2b$12$zww60U/9tdeJBhu.qREU6evCk1vnzBKwSgJvF5OfaNQH6z9s9j8Xq', '1995-01-01'),
(3, 'Cliente34', 'Apellido', 'usuario_34@example.com', '809-000-0034', '$2b$12$sr/KtGE/Msjn3KQOwipbIe61cblGoGlbCllw.8NdeemB9dqC7WseS', '1995-01-01'),
(3, 'Cliente35', 'Apellido', 'usuario_35@example.com', '809-000-0035', '$2b$12$mCCdLA3DuvEaQeHyM5ZV6uh56si6diaV2NlOIDJVO1hVnConGoaTu', '1995-01-01'),
(3, 'Cliente36', 'Apellido', 'usuario_36@example.com', '809-000-0036', '$2b$12$xvwA6sVmY/vnDsT4GUqwo.NGrNuywOmPIWb.GfnK2GE8YJuTagkc6', '1995-01-01'),
(3, 'Cliente37', 'Apellido', 'usuario_37@example.com', '809-000-0037', '$2b$12$tBPG.W4OeYJhMKw1yEDr8Onm5mtXbNBs2wUmySKQoS/XRCrOviIau', '1995-01-01'),
(3, 'Cliente38', 'Apellido', 'usuario_38@example.com', '809-000-0038', '$2b$12$Jq3EkJQsIrJ8yKsB9IhsC.em/GDdNP1GvthJeAKs6W1zNCdq2l/7G', '1995-01-01'),
(3, 'Cliente39', 'Apellido', 'usuario_39@example.com', '809-000-0039', '$2b$12$sqVdfWLoNqGuRbtjdrrPFOzC7iJ6MjuC53RO8HZSIdnKQLra8NWFm', '1995-01-01'),
(3, 'Cliente40', 'Apellido', 'usuario_40@example.com', '809-000-0040', '$2b$12$cKVJ.BBsynKV4zxKkMBOuuppn1Jr7jx7w0FL9YlsLtF2l3sBkc/n2', '1995-01-01'),
(3, 'Cliente41', 'Apellido', 'usuario_41@example.com', '809-000-0041', '$2b$12$urbC6QZnwWp5Dqo/R.AohOQ8mW9QlYebRj0xcY1CXToGR9gmGRD2K', '1995-01-01'),
(3, 'Cliente42', 'Apellido', 'usuario_42@example.com', '809-000-0042', '$2b$12$OtMUDUc5HxmPbP0aJh/6huO.ySOeDFzqQL2T/mkEwe5KsyjeeFrzm', '1995-01-01'),
(3, 'Cliente43', 'Apellido', 'usuario_43@example.com', '809-000-0043', '$2b$12$6jwaUJkJ3irYNSkJxcqyRO3KD.gtggE58JW31WmZ4X6RtT1hl3hPG', '1995-01-01'),
(3, 'Cliente44', 'Apellido', 'usuario_44@example.com', '809-000-0044', '$2b$12$vOd7zAVS8iWZp/2rJPCxhu8cCLqdJX6EG1o9NP0nA40uVPpZjyZ9S', '1995-01-01'),
(3, 'Cliente45', 'Apellido', 'usuario_45@example.com', '809-000-0045', '$2b$12$NNlc6s1KSYQEY7BQuQ9Hq.0XZIKg4MqsSKjDs5O8E0TcgSiNOyICu', '1995-01-01'),
(3, 'Cliente46', 'Apellido', 'usuario_46@example.com', '809-000-0046', '$2b$12$P1..aja8RQCsGbbRPlSERecm4ao4JfjqfdaoB1DJkC5SmW./2lEAy', '1995-01-01'),
(3, 'Cliente47', 'Apellido', 'usuario_47@example.com', '809-000-0047', '$2b$12$5jzbOej3aeZuYuWfkvaPBeB6gic7KaAKPabQ5DlaVCtrruuK8XFLq', '1995-01-01'),
(3, 'Cliente48', 'Apellido', 'usuario_48@example.com', '809-000-0048', '$2b$12$K1vspCIFZpPOjjYYrLeGROdjqUu4za1JS/PvAspeaf6hSDcCXzwgO', '1995-01-01'),
(3, 'Cliente49', 'Apellido', 'usuario_49@example.com', '809-000-0049', '$2b$12$B5b8iEuYTzPhSGdccnrPW.FDYzzc0j/vNrwCAhgs40iLrl8D452l2', '1995-01-01'),
(3, 'Cliente50', 'Apellido', 'usuario_50@example.com', '809-000-0050', '$2b$12$msFyGTX27V6Tq2Q6Bg9zEeiAJVkLk8.oIIqVjE6oljDkC6uo/z5Iu', '1995-01-01');

GO

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
