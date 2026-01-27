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
    DescripciónCorta NVARCHAR(600) NOT NULL,
    DescripciónLarga NVARCHAR(MAX) NOT NULL,
    LinkToBanner NVARCHAR(MAX) NOT NULL,
    LinkToBajante NVARCHAR(MAX) NOT NULL,
    LinkToTrailer NVARCHAR(MAX) NOT NULL,
    Activo BIT DEFAULT 1,
    FOREIGN KEY (IdClasificación) REFERENCES Clasificaciones(Id),
    FOREIGN KEY (IdIdioma) REFERENCES Idiomas(Id)
);

CREATE TABLE PelículaGénero (
    Id INT IDENTITY PRIMARY KEY,
    IdPelícula INT NOT NULL,
    IdGénero INT NOT NULL,
    FOREIGN KEY (IdPelícula) REFERENCES Películas(Id),
    FOREIGN KEY (IdGénero) REFERENCES Géneros(Id),
    UNIQUE(IdPelícula, IdGénero)
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
    UNIQUE (CorreoElectrónico)
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

GO

-- # Ingresar Datos

INSERT INTO Clasificaciones (Clasificación) VALUES
('N/S'),
('NR'),
('R/14'),
('R/16'),
('R/18');

INSERT INTO Idiomas (Idioma) VALUES
('Inglés'),
('Español');

INSERT INTO Géneros (Género) VALUES
('Acción'),
('Comedia'),
('Drama'),
('Animación'),
('Terror'),
('Ciencia Ficción'),
('Aventura');

INSERT INTO Cines (Cine, Dirección, Teléfono, GoogleMapIframeSrc)
VALUES (
    'Caribbean Cinemas Megacentro',
    'Megacentro, Santo Domingo Este',
    '809-544-2622',
    'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d288.0811221625557!2d-69.85722296657518!3d18.506539050388852!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8eaf86298704b5c9%3A0x9311b9d6fbdff46!2sCaribbean%20Cinemas%20Megaplex%2010!5e0!3m2!1ses-419!2sdo!4v1768609435800!5m2!1ses-419!2sdo'
);


INSERT INTO TipoDeSala (Tipo, PrecioAdulto, PrecioNiño) VALUES
('2D', 350.00, 200.00),
('3D', 450.00, 250.00),
('CxC', 600.00, 350.00);


INSERT INTO RolesDeUsuario (Rol) VALUES
('Administrador'),
('Encargado de Entrada'),
('Cliente');

INSERT INTO TipoBoletos (TipoBoleto) VALUES
('Adulto'),
('Niño');

INSERT INTO Películas (IdClasificación, IdIdioma, TítuloPelícula, DuraciónMinutos, DescripciónCorta, DescripciónLarga, LinkToBanner, LinkToBajante, LinkToTrailer) VALUES
(4, 2, 
'Avatar:Fuego y Cenizas', 197, 
'Tras los eventos de la guerra contra la RDA, Jake Sully y Neytiri deben enfrentar una amenaza interna sin precedentes: el Pueblo de la Ceniza. Esta tribu de Navi, marcada por la violencia y la ira, desafía la unidad de Pandora, obligando a la familia Sully a luchar en un entorno volcánico hostil para proteger su hogar.', 
'Expande el universo de Pandora explorando el lado más oscuro de sus habitantes nativos. La historia comienza poco después de la trágica pérdida de Neteyam, con una familia Sully vulnerable que busca refugio. Sin embargo, la paz se ve interrumpida por la aparición de Varang (interpretada por Oona Chaplin), la líder de una facción Navi que habita en regiones volcánicas y que ve la guerra de forma muy distinta a los Omaticaya o los Metkayina. A diferencia de las entregas anteriores, donde el conflicto principal era la invasión humana, esta película profundiza en los conflictos internos entre clanes. Mientras la RDA sigue presente bajo el mando de un reconstruido Coronel Quaritch, el verdadero peligro reside en el "fuego" emocional y físico de esta nueva tribu, que utiliza las cenizas y el calor volcánico para imponer su dominio. La narrativa explora temas de venganza, duelo y la compleja red de alianzas necesarias para evitar que Pandora se consuma desde adentro.',
'https://disney.images.edge.bamgrid.com/ripcut-delivery/v2/variant/disney/41ae7704-8740-4eb8-bb01-e4285e3b9011/compose?aspectRatio=1.78&format=webp&width=1200',
'https://cosmocentro.com/wp-content/uploads/2025/12/Avatar_Fuego_y_cenizas.jpg',
'https://www.youtube.com/watch?v=BlkNo-saOc0'),
(3, 2, 
'Anaconda', 100, 
'Dos amigos de la infancia en plena crisis de la mediana edad viajan al Amazonas para realizar un remake independiente de su película favorita, Anaconda. Lo que comienza como una producción caótica y de bajo presupuesto se convierte en una pesadilla real cuando una serpiente gigante verdadera comienza a cazarlos, obligándolos a luchar por sus vidas en un entorno donde la ficción se vuelve realidad.',
'Descripción Larga:La historia sigue a Doug (Jack Black), un videógrafo de bodas frustrado, y Griff (Paul Rudd), un actor cuya carrera está estancada. Desesperados por darle un sentido a sus vidas, deciden cumplir su sueño de la infancia: viajar a la selva de Brasil para rodar su propia versión de la película de 1997. Acompañados por sus amigos Kenny (Steve Zahn) y Claire (Thandiwe Newton), se adentran en el río Amazonas con un presupuesto minúsculo y un equipo técnico improvisado. La situación se complica cuando descubren que no están solos: una anaconda legendaria y asesina acecha la zona. La trama se vuelve cada vez más absurda y peligrosa al cruzarse con un equipo de rodaje profesional de Sony y enfrentarse a criminales locales, todo mientras intentan capturar las mejores tomas de su accidentada película antes de ser devorados.',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.landmarkcinemas.com%2Fmedia%2F427031%2Fanacondaofficialtrailer.jpg&f=1&nofb=1&ipt=1f6a4e789d61d8ad92c76982cee0326d520bea1484fa971d337652252a884131',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fanacondamovie.com%2Fimages%2Fanaconda_poster.jpg&f=1&nofb=1&ipt=3353eed3376a887237565058a855885cb2ed11dbe56b91e2b05fc79bed46d0dc',
'https://www.youtube.com/watch?v=Wh-d_zia8DY'),
(5, 2, 
'Cinco noches en Freddys 2', 104, 
'Un año después de los eventos en la pizzería de Freddy Fazbear, lo ocurrido se ha convertido en una leyenda urbana que inspira el festival local "Fazfest". Cuando Abby escapa para reencontrarse con sus "amigos" animatrónicos, desata una nueva serie de horrores que revelan los oscuros orígenes de Freddys y presentan una versión más avanzada y letal de las máquinas: los animatrónicos "Toy"',
'Ambientada un año después de la pesadilla sobrenatural de la primera entrega, Mike Schmidt (Josh Hutcherson) y la oficial Vanessa (Elizabeth Lail) intentan mantener a la pequeña Abby alejada de la verdad sobre los animatrónicos. Sin embargo, la curiosidad de Abby la lleva a buscar nuevamente a Freddy, Bonnie, Chica y Foxy, lo que la conduce al descubrimiento de un nuevo establecimiento con tecnología más moderna y reluciente, pero mucho más peligrosa. Esta secuela introduce a los modelos "Toy" y a la inquietante figura de The Marionette (el Títere), un animatrónico del local original que busca venganza. A medida que los secretos sobre el pasado de William Afton y el verdadero propósito de la pizzería salen a la luz, Mike debe enfrentarse no solo a los nuevos robots, sino también a versiones deterioradas y hostiles de sus antiguos conocidos, en una batalla por sobrevivir a cinco nuevas noches de terror absoluto.',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fp4.wallpaperbetter.com%2Fwallpaper%2F499%2F18%2F556%2Ffive-nights-at-freddy-s-five-nights-at-freddy-s-2-wallpaper-preview.jpg&f=1&nofb=1&ipt=07194bffeea192dedd44c617b94beec5c1a098843877b887d9b50de8eb142434',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fmoviesreview101.com%2Fwp-content%2Fuploads%2F2025%2F12%2Ffive-nights-at-freddies-2.png&f=1&nofb=1&ipt=3ad1920db6736ca64d4ff8736d673098d367c3aa736ce33c7b1adb0a46b210db',
'https://www.youtube.com/watch?v=E8M-iJ0p-Xk'),
(2, 2, 
'Grand Prix of Europe', 98, 
'El Gran Premio de Europa 2026 es la denominación que unifica la pasión del automovilismo en el continente, destacando este año por ser la temporada de transición previa a la llegada del nuevo Gran Premio de España en Madrid. Es un evento clave del Campeonato Mundial de la FIA que pone a prueba la aerodinámica de los monoplazas bajo el nuevo reglamento técnico de 2026, combinando velocidad extrema con la precisión técnica de los mejores pilotos del mundo.',
'Descripción Larga:La temporada 2026 de la Fórmula 1 marca el inicio de una nueva era tecnológica, con motores propulsados por combustibles 100% sostenibles y una mayor dependencia de la energía eléctrica. En este marco, el Grand Prix of Europe se consolida como el corazón de la gira europea, celebrándose en circuitos que representan la máxima exigencia para las escuderías.
Este evento no solo es una carrera de 300 kilómetros, sino un festival de innovación donde equipos como Red Bull, Ferrari y Mercedes debutan sus sistemas de aerodinámica activa. La edición de 2026 es especialmente significativa por ser el último año en que el trazado de Barcelona-Catalunya ostenta la exclusividad en la península antes de la entrada del circuito semi-urbano de Madrid, lo que ha generado una asistencia récord. El Gran Premio abarca tres días de competición intensa, desde las sesiones de prácticas y la clasificación Sprint, hasta la carrera dominical, donde la estrategia de neumáticos y el ahorro de energía eléctrica son los factores determinantes para alcanzar el podio.',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.kino-zeit.de%2Fsites%2Fdefault%2Ffiles%2Fstyles%2F2560_x_1440_header_%2Fpublic%2F2025-01%2Fgrand_prix_of_europe_2025_2.jpg%3Fitok%3DrbsQivAK&f=1&nofb=1&ipt=ac4192ede1c3aaac25b083ca6a168ff4e403f966672e5b26cf1ca92923acd593',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fm.media-amazon.com%2Fimages%2FM%2FMV5BNzZkNGZjNzEtNWY1Yy00NGE4LThmNjgtYzNjYzVmNDcwMmE5XkEyXkFqcGc%40._V1_FMjpg_UX1000_.jpg&f=1&nofb=1&ipt=0ab771a7200bb8596225b8c6d46c65c09475b6beb836de3f15656ad588b9fefe',
'https://www.youtube.com/watch?v=mvSrvfdF_D4'),
(3, 2, 
'Madias Hermanas', 100, 
'Medias Hermanas es una comedia que narra el accidentado encuentro entre Victoria y Maruja, dos mujeres que descubren, tras la muerte de su padre, que son hermanas. Obligadas a convivir para vender una propiedad compartida, ambas deberán superar sus profundas diferencias sociales y personales en un verano lleno de enredos, risas y revelaciones familiares.',
'La historia comienza con el funeral del patriarca de la familia, un evento que revela un secreto guardado por décadas: la existencia de dos hijas de mundos completamente opuestos. Victoria (Gianella Neyra) es una mujer de alta sociedad, refinada y algo rígida, mientras que Maruja (Magdyel Ugaz) es extrovertida, espontánea y proviene de un entorno popular. Para poder cobrar su herencia y resolver sus respectivas crisis financieras, ambas se ven obligadas a pasar un verano juntas en una casa de playa que deben reparar y vender. Lo que inicia como una convivencia forzada y llena de choques culturales y prejuicios, se transforma en un viaje de autoexploración. A través de situaciones hilarantes y momentos de vulnerabilidad, las "medias hermanas" descubren que tienen más en común de lo que pensaban, aprendiendo que la familia no solo se define por la sangre, sino por la capacidad de perdonar y aceptar al otro.',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fblogger.googleusercontent.com%2Fimg%2Fb%2FR29vZ2xl%2FAVvXsEhS71c_R_8-p_nUHiOfgMHGXS6gzRwnuUVK7NtaiFH6eeVUKpl4l7z-QVIe2z3V7JdCv7Q4Wt8frany8R0y9athiJUXXuSKemUf-m0Pn67sJlkAzyU_lmmtHLE4sw4sZJLQK6Ozhyhc6zfimbL9gayA03qm5zIlOKEvxIU72ojWqrwzpFWlS6MEFQ%2Fs1708%2FMedias%2520hermanas-Banner.jpg&f=1&nofb=1&ipt=ab9f51f5fa3d7ad5ca88c50a1f4d0af00b8e8fc029bccfdf90a7092c8070be5e',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fpics.filmaffinity.com%2Fmedias_hermanas-123299338-large.jpg&f=1&nofb=1&ipt=a35519ac115578d5febbbba969b5ddf3a6aecb026c3ba83f6bb9585b3334fb26',
'https://www.youtube.com/watch?v=7Y2DeBEt2Ew'),
(5, 2, 
'Primate', 89, 
'Primate es una comedia con tintes autobiográficos que sigue a William Days, un actor famoso que, al cumplir los 45 años, entra en una crisis de la mediana edad. Tras separarse y ser diagnosticado con diabetes tipo 2, William debe aprender a navegar su nueva soltería, la paternidad y su carrera en un mundo moderno que ya no comprende, dándose cuenta de que, en el fondo, sigue siendo un "primate" intentando evolucionar.',
'La serie profundiza en la vida de William Days (Christian Tappan), un hombre que aparentemente lo tenía todo: fama, una familia estable y una carrera sólida. Sin embargo, su mundo se desmorona cuando su esposa le pide el divorcio y su salud le da un aviso inesperado. Obligado a mudarse con su mejor amigo, William se enfrenta a la cruda realidad de ser un hombre de mediana edad en la era de las aplicaciones de citas, la corrección política y las redes sociales. A lo largo de los episodios, la trama explora con humor ácido y mucha honestidad temas como la masculinidad frágil, el miedo al envejecimiento y la búsqueda de la identidad más allá del éxito profesional. Con el apoyo de sus amigos Andrés y Joao, William intenta redescubrirse mientras lidia con las exigencias de sus hijos adolescentes y los absurdos de la industria del entretenimiento. Es una crónica humana sobre los errores, la resiliencia y la difícil tarea de madurar cuando todavía te sientes como un cavernícola perdido en el siglo XXI',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimages.thedirect.com%2Fmedia%2Farticle_full%2FPrimate_fixed_fixed.jpg&f=1&nofb=1&ipt=f5f4e21f73c863f1e59a2b8ff7d6a81589b7d94623e049bfccf7dc3867f2647b',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fpics.filmaffinity.com%2Fprimate-203311578-large.jpg&f=1&nofb=1&ipt=087ca74ba9ef52ae22c16d112388a052294b3862e350efae9a6037080872a46a',
'https://www.youtube.com/watch?v=nr1v2T1JMXY'),
(4, 2, 
'Vanilla Sky', 136,
'Vanilla Sky es un thriller psicológico que sigue la vida de David Aames, un joven y apuesto magnate editorial que lo tiene todo hasta que un trágico accidente automovilístico desfigura su rostro. A partir de ese momento, su realidad comienza a fragmentarse en una serie de visiones oníricas y paranoicas, llevándolo a cuestionar qué es real y qué es parte de una elaborada simulación mental en su búsqueda por el amor y la redención.',
'La historia presenta a David Aames (Tom Cruise), un heredero carismático y narcisista que vive una existencia privilegiada en Nueva York. Su vida cambia drásticamente cuando se enamora de Sofía (Penélope Cruz), la mujer de los sueños de su mejor amigo. Sin embargo, un arranque de celos de su antigua amante, Julianna (Cameron Diaz), provoca un accidente fatal que deja a David con el rostro severamente deformado. Tras someterse a una cirugía reconstructiva experimental, la vida de David parece volver a la normalidad, pero pronto la frontera entre sus sueños y la vigilia se disuelve. Acompañado por un psicólogo judicial (Kurt Russell) mientras es investigado por un asesinato que no recuerda, David debe navegar por un laberinto de recuerdos alterados y giros metafísicos. La película explora temas profundos como la criogenia, la identidad, el arrepentimiento y la posibilidad de elegir entre una "felicidad lúcida" o una realidad dolorosa, culminando en un final que redefine todo lo visto anteriormente.',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fntvb.tmsimg.com%2Fassets%2Fp28886_v_h10_ab.jpg%3Fw%3D960%26h%3D540&f=1&nofb=1&ipt=dbdef1e119a0383279e1439c669e7c8b873d6cc4921b2c60f509711d28d10330',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.dvdsreleasedates.com%2Fposters%2F800%2FV%2FVanilla-Sky-movie-poster.jpg&f=1&nofb=1&ipt=6dd2f7ca85cd6b3fc2e3f7c6568e9367989dd2371346ca4932bc41dee2158344',
'https://www.youtube.com/watch?v=rwJHvswJ-Qo'),
(5, 2, 
'El beso de la mujer araña', 128, 
'En una oscura celda de una prisión argentina durante la dictadura, dos hombres opuestos se ven obligados a convivir: Molina, un hombre homosexual encarcelado por "corromper a menores", y Valentín, un revolucionario político torturado. Para escapar de la brutal realidad, Molina narra tramas de películas clásicas, creando un lazo íntimo y transformador que desdibuja las fronteras entre la fantasía, el compromiso político y el amor prohibido.',
'La historia es un profundo estudio de la condición humana y la resistencia emocional. Luis Molina utiliza el cine como un mecanismo de defensa, transportando a su compañero de celda, Valentín Arregui, a mundos glamorosos y melodramáticos de la era dorada de Hollywood. Mientras Valentín desprecia inicialmente estas historias por considerarlas una distracción frívola de su lucha social, termina encontrando en ellas un refugio para su dolor físico y psicológico. A medida que avanza la trama, se revela una tensión moral: Molina ha sido presionado por las autoridades de la prisión para espiar a Valentín a cambio de su libertad. Sin embargo, la lealtad y el afecto que surge entre ambos transforma a Molina en una figura heroica y a Valentín en alguien más empático. La obra explora la sexualidad, el sacrificio y cómo la imaginación puede ser el arma más poderosa contra la opresión, culminando en un acto de amor que sella el destino de ambos de manera trágica pero trascendental.',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.dosismedia.com%2Fwp-content%2Fuploads%2F2025%2F10%2Fel-beso-de-la-mujer-arana-kiss-o.jpg&f=1&nofb=1&ipt=ca45feea913649bcf68e7ee91b7992847a341eaa6d7cfa5cbdcb0e3e088c818b',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.the-numbers.com%2Fimages%2Fmovies%2Fopusdata%2FKiss-of-the-Spider-Woman-(2025).jpg&f=1&nofb=1&ipt=09cb14b9565a96f08b1dc7c25df354959207e9793d80c323985bb6108b5b374f',
'https://www.youtube.com/watch?v=LY9SDi33zIU'),
(2, 2, 
'Se levanta el viento', 126, 
'Se levanta el viento es un relato biográfico ficcionalizado sobre Jiro Horikoshi, el ingeniero que diseñó los aviones de combate japoneses durante la Segunda Guerra Mundial. La película sigue su pasión por la aviación desde su infancia hasta la adultez, entrelazando sus sueños de ingeniería con una trágica historia de amor y el dilema moral de crear belleza en un mundo destinado a la destrucción.',
'La película narra décadas de la vida de Jiro Horikoshi, un hombre corto de vista que, al no poder ser piloto, decide dedicar su vida a diseñar aeronaves. Ambientada en una época de gran agitación social en Japón marcada por la Gran Depresión, la epidemia de tuberculosis y el devastador terremoto de Kanto de 1923, la trama muestra el ascenso de Jiro como un prodigio de la ingeniería aeronáutica. A medida que Jiro perfecciona sus diseños, se enamora de Naoko, una joven con una salud frágil que se convierte en su mayor apoyo emocional. La narrativa explora la melancolía del creador: Jiro desea fabricar aviones hermosos, pero se enfrenta a la dolorosa realidad de que sus creaciones serán utilizadas como herramientas de guerra. Con la estética visual característica de Hayao Miyazaki, la cinta es una oda a la perseverancia, al arte del diseño y a la fragilidad de la vida, planteando la pregunta de si vale la pena perseguir un sueño a pesar de las consecuencias que este pueda tener en el mundo real.',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2F1.bp.blogspot.com%2F-aU4kFhE4KA8%2FU2QNVFAcpPI%2FAAAAAAAAAlA%2FN7Z6ooMZysY%2Fs1600%2FEl-viento-se-levanta-21.jpg&f=1&nofb=1&ipt=589f87f484fb855af21419653c632f17927dea0cf02987b5478697e027b766ac',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fpics.filmaffinity.com%2FEl_viento_se_levanta-819618076-large.jpg&f=1&nofb=1&ipt=42fd4299dd67daf369d413482cc1c6a3403d17e11ee81e143bda9ba9b4aa6575',
'https://www.youtube.com/watch?v=YKdMqlGu0h0'),
(2, 2, 
'Tom y Jerry', 104,
'Tom y Jerry es la legendaria serie de comedia slapstick que narra la eterna e interminable persecución entre un gato doméstico, Tom, y un astuto ratón, Jerry. A través de ingeniosas trampas, caos físico y una banda sonora orquestal que dicta el ritmo de la acción, ambos personajes demuestran que, a pesar de sus constantes peleas, forman un vínculo inseparable donde la astucia siempre derrota a la fuerza bruta.',
'Creada originalmente por William Hanna y Joseph Barbera, Tom y Jerry se centra en la cómica rivalidad de sus dos protagonistas en diversos escenarios, que van desde hogares suburbanos clásicos hasta entornos futuristas o mundos de fantasía. Tom es un gato persistente pero desafortunado, cuyos planes para atrapar a su vecino terminan casi siempre en un desastre doloroso para él. Por otro lado, Jerry es un ratón ingenioso y sorprendentemente fuerte que utiliza el entorno a su favor para humillar a Tom, aunque en ocasiones ambos unen fuerzas contra amenazas externas. La serie se distingue por su casi total ausencia de diálogos, confiando en la expresividad visual, el diseño de sonido y una sincronización perfecta con la música clásica o jazz para contar sus historias. La franquicia ha evolucionado integrando técnicas de animación moderna que respetan el estilo 2D tradicional, manteniéndose relevante para nuevas generaciones al explorar temas de amistad improbable y resiliencia, consolidándose como el estándar de oro de la animación de persecución y comedia visual. ',
'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRM2qn1d28ob4YWKjFu9j0wATDDA7GTcbe2zQ&s',
'https://m.media-amazon.com/images/M/MV5BNjM3NzI5NjctNDc5MS00MTgwLWJkYTctNWY5NTlkYTQ4NjA1XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg',
'https://www.youtube.com/watch?v=kmq-uNePCgc'),
(2, 2, 
'De tal palo, tal astilla', 121,
'De tal palo, tal astilla es un conmovedor drama que narra la vida de Ryota, un exitoso arquitecto obsesionado con el trabajo, cuya vida se desmorona cuando descubre que su hijo biológico fue intercambiado al nacer en el hospital. Ante la decisión imposible de recuperar a su verdadero hijo o conservar al niño que ha criado durante seis años, Ryota debe cuestionar si la paternidad reside en los lazos de sangre o en el tiempo compartido.',
'La historia se centra en Ryota Nonomiya (Masaharu Fukuyama), un hombre ambicioso que cree que el éxito y la disciplina son los pilares de la familia. Su mundo perfecto cambia drásticamente cuando recibe una llamada del hospital informándole que su hijo, Keita, no es su hijo biológico. Debido a un error deliberado de una enfermera, Ryota y su esposa intercambiaron sus vidas con los Saiki, una familia de clase media mucho más humilde, relajada y afectuosa. La película explora el contraste entre las dos familias: la rigidez y el estatus de los Nonomiya frente a la alegría y el desorden de los Saiki. A medida que Ryota conoce a su hijo biológico, empieza a notar rasgos de su propia personalidad en él, pero también se da cuenta de la profunda conexión emocional que tiene con Keita. La narrativa se convierte en un viaje introspectivo sobre la naturaleza de la paternidad, el perdón y la redención, obligando al protagonista a decidir qué tipo de padre desea ser y qué es lo que realmente define a una familia en el Japón contemporáneo.',
'https://i.ytimg.com/vi/bmFOcrlHsxM/maxresdefault.jpg',
'https://caribbeancinemas.com/img/postersxlesp/10039.jpg',
'https://www.youtube.com/watch?v=bmFOcrlHsxM'),
(5, 2, 
'¡La novia! / The Bride', 93, 
'En el Chicago de la década de 1930, un solitario y melancólico Frankenstein (Christian Bale) viaja para pedir la ayuda del Dr. Euphronius en la creación de una compañera. Juntos, reviven a una joven asesinada (Jessie Buckley), dando origen a La Novia. Sin embargo, la mujer resucitada trasciende las intenciones de sus creadores, desarrollando una identidad salvaje, una sed de libertad radical y provocando un cambio social y romántico que nadie pudo prever.',
'Descripcis generosón Larga: Ambientada en una versión estilizada y oscura del Chicago de los años 30, la trama sigue al monstruo de Frankenstein, quien busca desesperadamente dejar de estar solo. Convence al Dr. Euphronius de realizar un experimento prohibido: utilizar el cuerpo de una mujer joven que fue víctima de la violencia para crear una pareja. Así nace La Novia, pero a diferencia de la criatura original, ella posee una chispa de rebelión y una autoconciencia que desafía el control masculino. La película se aleja del terror tradicional para convertirse en un drama psicológico con tintes de comedia negra y estética punk. Mientras los creadores esperan una compañera sumisa, ella se convierte en un símbolo de liberación, desafiando las normas de la época y atrayendo la atención de un joven entusiasta (interpretado por Peter Sarsgaard). La narrativa explora la obsesión, el deseo de pertenencia y las consecuencias de jugar a ser Dios, culminando en una explosión de caos visual y emocional que redefine la mitología del monstruo de Mary Shelley para el siglo XXI.',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fi.ytimg.com%2Fvi%2FIhgcUArO3Uo%2Fmaxresdefault.jpg&f=1&nofb=1&ipt=cce60192553fd9b4b53217ae6a1ee5175ae17829da62f62a3d692846fd0e99e6',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimage.tmdb.org%2Ft%2Fp%2Fw500%2F1TNcomNQIqY8vj05OyUDKusQymY.jpg&f=1&nofb=1&ipt=4648a6e7af52a81bdb340232451ac816370549fef37405bfb61cffa26c93ad7b',
'https://www.youtube.com/watch?v=XfMIn8l3tUU'),
(2, 2, 
'Hoppers', 90, 
'Hoppers es una comedia de ciencia ficción que sigue a Mabel, una joven amante de los animales que utiliza una nueva tecnología para "saltar" (transferir su conciencia) al cuerpo de un castor robótico hiperrealista. Lo que comienza como una misión encubierta para entender la vida silvestre se convierte en una épica aventura cuando Mabel se hace amiga de los animales reales y debe proteger su hábitat de los planes de un alcalde ambicioso.',
'La historia nos presenta a Mabel, una chica con una conexión especial con la naturaleza que aprovecha un avance tecnológico revolucionario: la capacidad de habitar cuerpos robóticos de animales para estudiarlos desde dentro. Al convertirse en una "Hopper", Mabel se infiltra en una comunidad de castores, descubriendo que estos animales tienen una estructura social compleja, personalidades vibrantes y sus propios problemas. La trama se complica cuando Mabel traba amistad con un castor real llamado Vinnie y descubre que el alcalde del pueblo, Jerry (interpretado por Jon Hamm), planea destruir el ecosistema local para un proyecto de desarrollo urbano. Dividida entre su vida humana y su nueva identidad en el reino animal, Mabel debe liderar a sus amigos peludos en una misión de sabotaje y rescate. La película explora con humor y corazón temas como la empatía entre especies, el impacto de la tecnología en el medio ambiente y lo que realmente significa ser uno mismo, sin importar la piel (o el pelaje) que habites.',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fi.pinimg.com%2Foriginals%2F31%2Fff%2Fd2%2F31ffd2ab1c76173677527ea64fc3b8b3.jpg&f=1&nofb=1&ipt=72b5d92390fd68be8d670bb6f25fa7aa86210527b466b4808cb04a4c320f4cdf',
'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fthejoyofmovies.ca%2Fwp-content%2Fuploads%2F2025%2F11%2Fhoppers_canada_ka_70x100.jpg&f=1&nofb=1&ipt=31baebac93093e6a62e51808ae3c5f3e2e1dbf98a123cca3cd8f13c892e59296',
'https://www.youtube.com/watch?v=AsW4KkFfifw');

INSERT INTO PelículaGénero (IdPelícula, IdGénero) VALUES
-- 1. Avatar: Fuego y Cenizas
(1, 1), -- Acción
(1, 6), -- Ciencia Ficción
(1, 7), -- Aventura
-- 2. Anaconda
(2, 5), -- Terror
(2, 7), -- Aventura
(2, 2), -- Comedia
-- 3. Cinco noches en Freddys 2
(3, 5), -- Terror
(3, 6), -- Ciencia Ficción
-- 4. Grand Prix of Europe
(4, 1), -- Acción
(4, 7), -- Aventura
(4, 3), -- Drama
-- 5. Medias Hermanas
(5, 2), -- Comedia
(5, 3), -- Drama
-- 6. Primate
(6, 2), -- Comedia
(6, 3), -- Drama
-- 7. Vanilla Sky
(7, 3), -- Drama
(7, 6), -- Ciencia Ficción
-- 8. El beso de la mujer araña
(8, 3), -- Drama
-- 9. Se levanta el viento
(9, 3), -- Drama
(9, 4), -- Animación
-- 10. Tom y Jerry
(10, 2), -- Comedia
(10, 4), -- Animación
(10, 7), -- Aventura
-- 11. De tal palo, tal astilla
(11, 3), -- Drama
-- 12. ¡La novia! / The Bride
(12, 3), -- Drama
(12, 5), -- Terror
(12, 6), -- Ciencia Ficción
-- 13. Hoppers
(13, 2), -- Comedia
(13, 4), -- Animación
(13, 6), -- Ciencia Ficción
(13, 7); -- Aventura


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


INSERT INTO Salas (IdCine, IdTipo, NúmeroDeSala) VALUES
(1, 1, 1), -- Sala 1: 2D
(1, 1, 2), -- Sala 2: 2D
(1, 2, 3), -- Sala 3: 3D
(1, 2, 4), -- Sala 4: 3D
(1, 3, 5), -- Sala 5: CxC
(1, 3, 6); -- Sala 6: CxC

-- Declaración de variables para el control de los bucles
DECLARE @Sala INT;
DECLARE @Fila INT; -- Solo declaramos aquí
DECLARE @ColIndice INT;
DECLARE @Codigo NVARCHAR(3);

BEGIN
	SET @Sala = 1; 
    WHILE @Sala <= 6
    BEGIN
	    SET @Fila = 1; 
        WHILE @Fila <= 25
        BEGIN
            SET @ColIndice = 0; 
            WHILE @ColIndice < 12
            BEGIN
                SET @Codigo = CHAR(65 + @ColIndice) + CAST(@Fila AS NVARCHAR(2))
                INSERT INTO Asientos (IdSala, CódigoAsiento)
                VALUES (@Sala, @Codigo);
                SET @ColIndice = @ColIndice + 1;
            END
            SET @Fila = @Fila + 1;
        END
        SET @Sala = @Sala + 1;
    END
END
PRINT 'Inserción de 1800 asientos completada con éxito.';

INSERT INTO Funciones (IdPelícula, IdSala, FechaHora) VALUES
-- Lunes (2026-01-19)
(1, 1, '2026-01-19 17:00:00'),
(2, 2, '2026-01-19 17:25:00'),
(3, 3, '2026-01-19 18:00:00'),
(4, 4, '2026-01-19 18:00:00'),
(5, 5, '2026-01-19 18:00:00'),
(6, 6, '2026-01-19 18:00:00'),
(7, 3, '2026-01-19 20:05:00'),
(8, 4, '2026-01-19 20:10:00'),
(9, 5, '2026-01-19 20:10:00'),
(10, 6, '2026-01-19 18:30:00'),
(1, 1, '2026-01-19 20:45:00'),
(2, 2, '2026-01-19 19:30:00'),
-- Martes (2026-01-20)
(1, 1, '2026-01-20 17:00:00'),
(2, 2, '2026-01-20 17:25:00'),
(3, 3, '2026-01-20 18:00:00'),
(4, 4, '2026-01-20 18:00:00'),
(5, 5, '2026-01-20 18:00:00'),
(6, 6, '2026-01-20 18:00:00'),
(7, 3, '2026-01-20 20:05:00'),
(8, 4, '2026-01-20 20:10:00'),
(9, 5, '2026-01-20 20:10:00'),
(10, 6, '2026-01-20 18:30:00'),
(1, 1, '2026-01-20 20:45:00'),
(2, 2, '2026-01-20 19:30:00'),
-- Miercoles (2026-01-21)
(1, 1, '2026-01-21 17:00:00'),
(2, 2, '2026-01-21 17:25:00'),
(3, 3, '2026-01-21 18:00:00'),
(4, 4, '2026-01-21 18:00:00'),
(5, 5, '2026-01-21 18:00:00'),
(6, 6, '2026-01-21 18:00:00'),
(7, 3, '2026-01-21 20:05:00'),
(8, 4, '2026-01-21 20:10:00'),
(9, 5, '2026-01-21 20:10:00'),
(10, 6, '2026-01-21 18:30:00'),
(1, 1, '2026-01-21 20:45:00'),
(2, 2, '2026-01-21 19:30:00'),
-- Jueves (2026-01-22)
(1, 1, '2026-01-22 17:00:00'),
(2, 2, '2026-01-22 17:25:00'),
(3, 3, '2026-01-22 18:00:00'),
(4, 4, '2026-01-22 18:00:00'),
(5, 5, '2026-01-22 18:00:00'),
(6, 6, '2026-01-22 18:00:00'),
(7, 3, '2026-01-22 20:05:00'),
(8, 4, '2026-01-22 20:10:00'),
(9, 5, '2026-01-22 20:10:00'),
(10, 6, '2026-01-22 18:30:00'),
(1, 1, '2026-01-22 20:45:00'),
(2, 2, '2026-01-22 19:30:00'),
-- Viernes (2026-01-23)
(1, 1, '2026-01-23 17:00:00'),
(2, 2, '2026-01-23 17:25:00'),
(3, 3, '2026-01-23 18:00:00'),
(4, 4, '2026-01-23 18:00:00'),
(5, 5, '2026-01-23 18:00:00'),
(6, 6, '2026-01-23 18:00:00'),
(7, 3, '2026-01-23 20:05:00'),
(8, 4, '2026-01-23 20:10:00'),
(9, 5, '2026-01-23 20:10:00'),
(10, 6, '2026-01-23 18:30:00'),
(1, 1, '2026-01-23 20:45:00'),
(2, 2, '2026-01-23 19:30:00'),
-- Sabado (2026-01-24)
(1, 1, '2026-01-24 17:00:00'),
(2, 2, '2026-01-24 17:25:00'),
(3, 3, '2026-01-24 18:00:00'),
(4, 4, '2026-01-24 18:00:00'),
(5, 5, '2026-01-24 18:00:00'),
(6, 6, '2026-01-24 18:00:00'),
(7, 3, '2026-01-24 20:05:00'),
(8, 4, '2026-01-24 20:10:00'),
(9, 5, '2026-01-24 20:10:00'),
(10, 6, '2026-01-24 18:30:00'),
(1, 1, '2026-01-24 20:45:00'),
(2, 2, '2026-01-24 19:30:00'),
-- Domingo (2026-01-25)
(1, 1, '2026-01-25 17:00:00'),
(2, 2, '2026-01-25 17:25:00'),
(3, 3, '2026-01-25 18:00:00'),
(4, 4, '2026-01-25 18:00:00'),
(5, 5, '2026-01-25 18:00:00'),
(6, 6, '2026-01-25 18:00:00'),
(7, 3, '2026-01-25 20:05:00'),
(8, 4, '2026-01-25 20:10:00'),
(9, 5, '2026-01-25 20:10:00'),
(10, 6, '2026-01-25 18:30:00'),
(1, 1, '2026-01-25 20:45:00'),
(2, 2, '2026-01-25 19:30:00'),
-- Lunes (2026-01-26)
(1, 1, '2026-01-26 17:00:00'),
(2, 2, '2026-01-26 17:25:00'),
(3, 3, '2026-01-26 18:00:00'),
(4, 4, '2026-01-26 18:00:00'),
(5, 5, '2026-01-26 18:00:00'),
(6, 6, '2026-01-26 18:00:00'),
(7, 3, '2026-01-26 20:05:00'),
(8, 4, '2026-01-26 20:10:00'),
(9, 5, '2026-01-26 20:10:00'),
(10, 6, '2026-01-26 18:30:00'),
(1, 1, '2026-01-26 20:45:00'),
(2, 2, '2026-01-26 19:30:00'),
-- Martes (2026-01-27)
(1, 1, '2026-01-27 17:00:00'),
(2, 2, '2026-01-27 17:25:00'),
(3, 3, '2026-01-27 18:00:00'),
(4, 4, '2026-01-27 18:00:00'),
(5, 5, '2026-01-27 18:00:00'),
(6, 6, '2026-01-27 18:00:00'),
(7, 3, '2026-01-27 20:05:00'),
(8, 4, '2026-01-27 20:10:00'),
(9, 5, '2026-01-27 20:10:00'),
(10, 6, '2026-01-27 18:30:00'),
(1, 1, '2026-01-27 20:45:00'),
(2, 2, '2026-01-27 19:30:00'),
-- Miercoles (2026-01-28)
(1, 1, '2026-01-28 17:00:00'),
(2, 2, '2026-01-28 17:25:00'),
(3, 3, '2026-01-28 18:00:00'),
(4, 4, '2026-01-28 18:00:00'),
(5, 5, '2026-01-28 18:00:00'),
(6, 6, '2026-01-28 18:00:00'),
(7, 3, '2026-01-28 20:05:00'),
(8, 4, '2026-01-28 20:10:00'),
(9, 5, '2026-01-28 20:10:00'),
(10, 6, '2026-01-28 18:30:00'),
(1, 1, '2026-01-28 20:45:00'),
(2, 2, '2026-01-28 19:30:00'),
-- Funciones futuras
-- Jueves (2026-03-05)
(11, 1, '2026-03-05 18:00:00'),
(12, 2, '2026-03-05 18:00:00'),
(13, 3, '2026-03-05 18:00:00'),
(11, 4, '2026-03-05 18:00:00'),
(12, 5, '2026-03-05 18:00:00'),
(13, 6, '2026-03-05 18:00:00'),
-- Viernes (2026-03-06)
(11, 1, '2026-03-06 18:00:00'),
(12, 2, '2026-03-06 18:00:00'),
(13, 3, '2026-03-06 18:00:00'),
(11, 4, '2026-03-06 18:00:00'),
(12, 5, '2026-03-06 18:00:00'),
(13, 6, '2026-03-06 18:00:00'),
-- Sabado (2026-03-07)
(11, 1, '2026-03-07 18:00:00'),
(12, 2, '2026-03-07 18:00:00'),
(13, 3, '2026-03-07 18:00:00'),
(11, 4, '2026-03-07 18:00:00'),
(12, 5, '2026-03-07 18:00:00'),
(13, 6, '2026-03-07 18:00:00');


-- Insert Boletos

INSERT INTO Boletos (
    IdFunción,
    IdAsiento,
    IdUsuario,
    IdTipoBoleto,
    FechaCreacion,
    ValorPagado
)
SELECT
    f.IdFuncion,
    a.IdAsiento,
    3 + (ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) % 50) AS IdUsuario,
    CASE 
        WHEN a.IdAsiento % 2 = 0 THEN 1 ELSE 2
    END AS IdTipoBoleto,
    DATEADD(DAY, -5, '2026-01-25') AS FechaCreacion,
    CASE 
        WHEN a.IdAsiento % 2 = 0 THEN 350 ELSE 200
    END AS ValorPagado
FROM (
    SELECT number AS IdFuncion
    FROM master..spt_values
    WHERE type = 'P'
      AND number BETWEEN 1 AND 138
) f
CROSS JOIN (
    SELECT number AS IdAsiento
    FROM master..spt_values
    WHERE type = 'P'
      AND number BETWEEN 1 AND 150
) a;


-- Insert BoletosCancelados

INSERT INTO BoletosCancelados (
    IdBoleto,
    FechaCancelacion,
    ValorAcreditado,
    Canjeado
)
SELECT TOP (10) PERCENT
    b.Id,
    GETDATE(),
    b.ValorPagado,
    0
FROM Boletos b
WHERE NOT EXISTS (
    SELECT 1
    FROM BoletosCancelados bc
    WHERE bc.IdBoleto = b.Id
)
ORDER BY NEWID();


-- Insert BoletosUsados

INSERT INTO BoletosUsados (
    IdBoleto,
    IdEncargado,
    FechaUso
)
SELECT
    b.Id,
    1 AS IdEncargado,
    GETDATE() AS FechaUso
FROM Boletos b
WHERE b.Id NOT IN (
    SELECT IdBoleto
    FROM BoletosCancelados
)
AND b.Id NOT IN (
    SELECT IdBoleto
    FROM BoletosUsados
)
AND b.Id <= (
    SELECT CAST(COUNT(*) * 0.85 AS INT)
    FROM Boletos
);

GO

-- # Create vistas a usar

-- ========== Índices optimizados para dashboard y controladores existentes ================

CREATE NONCLUSTERED INDEX IX_Funciones_FechaHora_IdPelicula_Activo
ON Funciones(FechaHora, IdPelícula, Activo)
INCLUDE (IdSala);

CREATE NONCLUSTERED INDEX IX_Boletos_IdFuncion_IdAsiento_IdUsuario
ON Boletos(IdFunción, IdAsiento, IdUsuario)
INCLUDE (IdTipoBoleto, ValorPagado, FechaCreacion);

CREATE NONCLUSTERED INDEX IX_BoletosCancelados_IdBoleto
ON BoletosCancelados(IdBoleto)
INCLUDE (FechaCancelacion, ValorAcreditado, Canjeado);

CREATE NONCLUSTERED INDEX IX_BoletosUsados_IdBoleto
ON BoletosUsados(IdBoleto)
INCLUDE (IdEncargado, FechaUso);

CREATE NONCLUSTERED INDEX IX_Peliculas_IdClasificacion_IdIdioma_Activo
ON Películas(IdClasificación, IdIdioma, Activo)
INCLUDE (TítuloPelícula, DuraciónMinutos, LinkToBanner);

CREATE NONCLUSTERED INDEX IX_Salas_IdCine_IdTipo_Activo
ON Salas(IdCine, IdTipo, Activo)
INCLUDE (NúmeroDeSala);

CREATE NONCLUSTERED INDEX IX_Asientos_IdSala_Activo
ON Asientos(IdSala, Activo)
INCLUDE (CódigoAsiento);

CREATE NONCLUSTERED INDEX IX_PeliculaGenero_IdPelicula_IdGenero
ON PelículaGénero(IdPelícula, IdGénero);

CREATE NONCLUSTERED INDEX IX_Usuarios_IdRol_CorreoElectronico
ON Usuarios(IdRol, CorreoElectrónico)
INCLUDE (Nombre, Apellidos, ContraseñaHash);

-- Índice compuesto para búsquedas por fecha en funciones
CREATE NONCLUSTERED INDEX IX_Funciones_FechaHora_Activo
ON Funciones(FechaHora, Activo)
INCLUDE (IdPelícula, IdSala);

-- Índice para consultas de ocupación
CREATE NONCLUSTERED INDEX IX_Asientos_Sala_Activo
ON Asientos(IdSala, Activo);


-- =============== FUNCIONES PARA DASHBOARD ============================

GO

-- # Funciones para Dashboard

-- Función para obtener ingresos diarios/semanales/mensuales
CREATE OR ALTER FUNCTION dbo.fn_Dashboard_Ingresos (
    @FechaInicio DATE,
    @FechaFin DATE,
    @CineIds NVARCHAR(MAX) = NULL,
    @GeneroIds NVARCHAR(MAX) = NULL,
    @PeliculaIds NVARCHAR(MAX) = NULL,
    @FuncionIds NVARCHAR(MAX) = NULL,
    @DiasSemana NVARCHAR(50) = NULL,
    @Agrupacion NVARCHAR(10) = 'dia' -- 'dia', 'semana', 'mes'
)
RETURNS TABLE
AS
RETURN
WITH Filtros AS (
    SELECT 
        f.Id AS FuncionId,
        f.FechaHora,
        f.IdPelícula,
        f.IdSala,
        s.IdCine,
        p.TítuloPelícula,
        pg.IdGénero
    FROM Funciones f
    INNER JOIN Salas s ON f.IdSala = s.Id
    INNER JOIN Películas p ON f.IdPelícula = p.Id
    LEFT JOIN PelículaGénero pg ON p.Id = pg.IdPelícula
    WHERE f.FechaHora >= @FechaInicio 
        AND f.FechaHora < DATEADD(day, 1, @FechaFin)
        AND f.Activo = 1
        AND (@CineIds IS NULL OR s.IdCine IN (SELECT value FROM STRING_SPLIT(@CineIds, ',')))
        AND (@GeneroIds IS NULL OR pg.IdGénero IN (SELECT value FROM STRING_SPLIT(@GeneroIds, ',')))
        AND (@PeliculaIds IS NULL OR p.Id IN (SELECT value FROM STRING_SPLIT(@PeliculaIds, ',')))
        AND (@FuncionIds IS NULL OR f.Id IN (SELECT value FROM STRING_SPLIT(@FuncionIds, ',')))
        AND (@DiasSemana IS NULL OR DATEPART(weekday, f.FechaHora) IN (SELECT value FROM STRING_SPLIT(@DiasSemana, ',')))
),
IngresosDiarios AS (
    SELECT 
        CASE @Agrupacion
            WHEN 'dia' THEN CONVERT(DATE, f.FechaHora)
            WHEN 'semana' THEN DATEADD(day, 1 - DATEPART(weekday, f.FechaHora), CONVERT(DATE, f.FechaHora))
            WHEN 'mes' THEN DATEFROMPARTS(YEAR(f.FechaHora), MONTH(f.FechaHora), 1)
        END AS Periodo,
        b.ValorPagado,
        DATEPART(weekday, f.FechaHora) AS DiaSemana,
        DATEPART(week, f.FechaHora) AS Semana,
        DATEPART(month, f.FechaHora) AS Mes
    FROM Filtros f
    INNER JOIN Boletos b ON f.FuncionId = b.IdFunción
    WHERE NOT EXISTS (
        SELECT 1 FROM BoletosCancelados bc 
        WHERE bc.IdBoleto = b.Id
    )
)
SELECT 
    Periodo,
    SUM(ValorPagado) AS Ingresos,
    COUNT(*) AS BoletosVendidos,
    AVG(CASE WHEN DiaSemana IS NOT NULL THEN DiaSemana ELSE NULL END) AS DiaSemanaPromedio,
    MAX(Semana) AS SemanaNumero,
    MAX(Mes) AS MesNumero
FROM IngresosDiarios
GROUP BY Periodo
ORDER BY Periodo;

GO

-- Función para obtener ocupación de salas
CREATE OR ALTER FUNCTION dbo.fn_Dashboard_Ocupacion (
    @FechaInicio DATE,
    @FechaFin DATE,
    @CineIds NVARCHAR(MAX) = NULL,
    @GeneroIds NVARCHAR(MAX) = NULL,
    @PeliculaIds NVARCHAR(MAX) = NULL,
    @FuncionIds NVARCHAR(MAX) = NULL,
    @DiasSemana NVARCHAR(50) = NULL,
    @Agrupacion NVARCHAR(10) = 'dia'
)
RETURNS TABLE
AS
RETURN
WITH Filtros AS (
    SELECT 
        f.Id AS FuncionId,
        f.FechaHora,
        f.IdPelícula,
        f.IdSala,
        s.IdCine,
        p.TítuloPelícula,
        pg.IdGénero
    FROM Funciones f
    INNER JOIN Salas s ON f.IdSala = s.Id
    INNER JOIN Películas p ON f.IdPelícula = p.Id
    LEFT JOIN PelículaGénero pg ON p.Id = pg.IdPelícula
    WHERE f.FechaHora >= @FechaInicio 
        AND f.FechaHora < DATEADD(day, 1, @FechaFin)
        AND f.Activo = 1
        AND (@CineIds IS NULL OR s.IdCine IN (SELECT value FROM STRING_SPLIT(@CineIds, ',')))
        AND (@GeneroIds IS NULL OR pg.IdGénero IN (SELECT value FROM STRING_SPLIT(@GeneroIds, ',')))
        AND (@PeliculaIds IS NULL OR p.Id IN (SELECT value FROM STRING_SPLIT(@PeliculaIds, ',')))
        AND (@FuncionIds IS NULL OR f.Id IN (SELECT value FROM STRING_SPLIT(@FuncionIds, ',')))
        AND (@DiasSemana IS NULL OR DATEPART(weekday, f.FechaHora) IN (SELECT value FROM STRING_SPLIT(@DiasSemana, ',')))
),
CapacidadFunciones AS (
    SELECT 
        f.FuncionId,
        f.FechaHora,
        f.IdSala,
        COUNT(a.Id) AS CapacidadTotal
    FROM Filtros f
    INNER JOIN Asientos a ON f.IdSala = a.IdSala AND a.Activo = 1
    GROUP BY f.FuncionId, f.FechaHora, f.IdSala
),
BoletosVendidos AS (
    SELECT 
        f.FuncionId,
        COUNT(b.Id) AS BoletosVendidos
    FROM Filtros f
    INNER JOIN Boletos b ON f.FuncionId = b.IdFunción
    WHERE NOT EXISTS (
        SELECT 1 FROM BoletosCancelados bc 
        WHERE bc.IdBoleto = b.Id
    )
    GROUP BY f.FuncionId
),
DatosAgrupados AS (
    SELECT 
        cf.FuncionId,
        cf.FechaHora,
        cf.CapacidadTotal,
        ISNULL(bv.BoletosVendidos, 0) AS BoletosVendidos,
        CASE @Agrupacion
            WHEN 'dia' THEN CONVERT(DATE, cf.FechaHora)
            WHEN 'semana' THEN DATEADD(day, 1 - DATEPART(weekday, cf.FechaHora), CONVERT(DATE, cf.FechaHora))
            WHEN 'mes' THEN DATEFROMPARTS(YEAR(cf.FechaHora), MONTH(cf.FechaHora), 1)
        END AS Periodo
    FROM CapacidadFunciones cf
    LEFT JOIN BoletosVendidos bv ON cf.FuncionId = bv.FuncionId
)
SELECT 
    Periodo,
    SUM(CapacidadTotal) AS CapacidadTotal,
    SUM(BoletosVendidos) AS BoletosVendidos,
    CASE 
        WHEN SUM(CapacidadTotal) > 0 
        THEN (SUM(BoletosVendidos) * 100.0 / SUM(CapacidadTotal)) 
        ELSE 0 
    END AS PorcentajeOcupacion
FROM DatosAgrupados
GROUP BY Periodo
ORDER BY Periodo;

GO

-- Función para obtener porcentaje de boletos usados
CREATE OR ALTER FUNCTION dbo.fn_Dashboard_BoletosUsados (
    @FechaInicio DATE,
    @FechaFin DATE,
    @CineIds NVARCHAR(MAX) = NULL,
    @GeneroIds NVARCHAR(MAX) = NULL,
    @PeliculaIds NVARCHAR(MAX) = NULL,
    @FuncionIds NVARCHAR(MAX) = NULL,
    @DiasSemana NVARCHAR(50) = NULL,
    @Agrupacion NVARCHAR(10) = 'dia'
)
RETURNS TABLE
AS
RETURN
WITH Filtros AS (
    SELECT 
        f.Id AS FuncionId,
        f.FechaHora,
        f.IdPelícula,
        f.IdSala,
        s.IdCine,
        p.TítuloPelícula,
        pg.IdGénero
    FROM Funciones f
    INNER JOIN Salas s ON f.IdSala = s.Id
    INNER JOIN Películas p ON f.IdPelícula = p.Id
    LEFT JOIN PelículaGénero pg ON p.Id = pg.IdPelícula
    WHERE f.FechaHora >= @FechaInicio 
        AND f.FechaHora < DATEADD(day, 1, @FechaFin)
        AND f.Activo = 1
        AND (@CineIds IS NULL OR s.IdCine IN (SELECT value FROM STRING_SPLIT(@CineIds, ',')))
        AND (@GeneroIds IS NULL OR pg.IdGénero IN (SELECT value FROM STRING_SPLIT(@GeneroIds, ',')))
        AND (@PeliculaIds IS NULL OR p.Id IN (SELECT value FROM STRING_SPLIT(@PeliculaIds, ',')))
        AND (@FuncionIds IS NULL OR f.Id IN (SELECT value FROM STRING_SPLIT(@FuncionIds, ',')))
        AND (@DiasSemana IS NULL OR DATEPART(weekday, f.FechaHora) IN (SELECT value FROM STRING_SPLIT(@DiasSemana, ',')))
),
BoletosTotales AS (
    SELECT 
        f.FuncionId,
        f.FechaHora,
        COUNT(b.Id) AS BoletosTotales,
        COUNT(bu.Id) AS BoletosUsados,
        CASE @Agrupacion
            WHEN 'dia' THEN CONVERT(DATE, f.FechaHora)
            WHEN 'semana' THEN DATEADD(day, 1 - DATEPART(weekday, f.FechaHora), CONVERT(DATE, f.FechaHora))
            WHEN 'mes' THEN DATEFROMPARTS(YEAR(f.FechaHora), MONTH(f.FechaHora), 1)
        END AS Periodo
    FROM Filtros f
    INNER JOIN Boletos b ON f.FuncionId = b.IdFunción
    LEFT JOIN BoletosUsados bu ON b.Id = bu.IdBoleto
    WHERE NOT EXISTS (
        SELECT 1 FROM BoletosCancelados bc 
        WHERE bc.IdBoleto = b.Id
    )
    GROUP BY f.FuncionId, f.FechaHora
)
SELECT 
    Periodo,
    SUM(BoletosTotales) AS BoletosTotales,
    SUM(BoletosUsados) AS BoletosUsados,
    CASE 
        WHEN SUM(BoletosTotales) > 0 
        THEN (SUM(BoletosUsados) * 100.0 / SUM(BoletosTotales)) 
        ELSE 0 
    END AS PorcentajeUsados
FROM BoletosTotales
GROUP BY Periodo
ORDER BY Periodo;

GO

-- Función para obtener porcentaje de cancelaciones
CREATE OR ALTER FUNCTION dbo.fn_Dashboard_Cancelaciones (
    @FechaInicio DATE,
    @FechaFin DATE,
    @CineIds NVARCHAR(MAX) = NULL,
    @GeneroIds NVARCHAR(MAX) = NULL,
    @PeliculaIds NVARCHAR(MAX) = NULL,
    @FuncionIds NVARCHAR(MAX) = NULL,
    @DiasSemana NVARCHAR(50) = NULL,
    @Agrupacion NVARCHAR(10) = 'dia'
)
RETURNS TABLE
AS
RETURN
WITH Filtros AS (
    SELECT 
        f.Id AS FuncionId,
        f.FechaHora,
        f.IdPelícula,
        f.IdSala,
        s.IdCine,
        p.TítuloPelícula,
        pg.IdGénero
    FROM Funciones f
    INNER JOIN Salas s ON f.IdSala = s.Id
    INNER JOIN Películas p ON f.IdPelícula = p.Id
    LEFT JOIN PelículaGénero pg ON p.Id = pg.IdPelícula
    WHERE f.FechaHora >= @FechaInicio 
        AND f.FechaHora < DATEADD(day, 1, @FechaFin)
        AND f.Activo = 1
        AND (@CineIds IS NULL OR s.IdCine IN (SELECT value FROM STRING_SPLIT(@CineIds, ',')))
        AND (@GeneroIds IS NULL OR pg.IdGénero IN (SELECT value FROM STRING_SPLIT(@GeneroIds, ',')))
        AND (@PeliculaIds IS NULL OR p.Id IN (SELECT value FROM STRING_SPLIT(@PeliculaIds, ',')))
        AND (@FuncionIds IS NULL OR f.Id IN (SELECT value FROM STRING_SPLIT(@FuncionIds, ',')))
        AND (@DiasSemana IS NULL OR DATEPART(weekday, f.FechaHora) IN (SELECT value FROM STRING_SPLIT(@DiasSemana, ',')))
),
BoletosVendidos AS (
    SELECT 
        f.FuncionId,
        f.FechaHora,
        COUNT(b.Id) AS BoletosVendidos,
        COUNT(bc.Id) AS BoletosCancelados,
        CASE @Agrupacion
            WHEN 'dia' THEN CONVERT(DATE, f.FechaHora)
            WHEN 'semana' THEN DATEADD(day, 1 - DATEPART(weekday, f.FechaHora), CONVERT(DATE, f.FechaHora))
            WHEN 'mes' THEN DATEFROMPARTS(YEAR(f.FechaHora), MONTH(f.FechaHora), 1)
        END AS Periodo
    FROM Filtros f
    INNER JOIN Boletos b ON f.FuncionId = b.IdFunción
    LEFT JOIN BoletosCancelados bc ON b.Id = bc.IdBoleto
    GROUP BY f.FuncionId, f.FechaHora
)
SELECT 
    Periodo,
    SUM(BoletosVendidos) AS BoletosVendidos,
    SUM(BoletosCancelados) AS BoletosCancelados,
    CASE 
        WHEN SUM(BoletosVendidos) > 0 
        THEN (SUM(BoletosCancelados) * 100.0 / SUM(BoletosVendidos)) 
        ELSE 0 
    END AS PorcentajeCancelaciones
FROM BoletosVendidos
GROUP BY Periodo
ORDER BY Periodo;

GO

-- Función para obtener datos RAW para Excel
CREATE OR ALTER FUNCTION dbo.fn_Dashboard_RawData (
    @FechaInicio DATE,
    @FechaFin DATE,
    @CineIds NVARCHAR(MAX) = NULL,
    @GeneroIds NVARCHAR(MAX) = NULL,
    @PeliculaIds NVARCHAR(MAX) = NULL,
    @FuncionIds NVARCHAR(MAX) = NULL,
    @DiasSemana NVARCHAR(50) = NULL
)
RETURNS TABLE
AS
RETURN
SELECT 
    f.Id AS FuncionId,
    f.FechaHora,
    c.Cine,
    c.Dirección AS DireccionCine,
    s.NúmeroDeSala,
    ts.Tipo AS TipoSala,
    p.TítuloPelícula AS Pelicula,
    cl.Clasificación,
    i.Idioma,
    g.Género,
    b.Id AS BoletoId,
    b.FechaCreacion,
    tb.TipoBoleto,
    b.ValorPagado,
    CASE WHEN bc.Id IS NOT NULL THEN 1 ELSE 0 END AS Cancelado,
    bc.FechaCancelacion,
    bc.ValorAcreditado,
    CASE WHEN bu.Id IS NOT NULL THEN 1 ELSE 0 END AS Usado,
    bu.FechaUso,
    u.Nombre + ' ' + u.Apellidos AS Cliente,
    a.CódigoAsiento
FROM Funciones f
INNER JOIN Salas s ON f.IdSala = s.Id
INNER JOIN Cines c ON s.IdCine = c.Id
INNER JOIN TipoDeSala ts ON s.IdTipo = ts.Id
INNER JOIN Películas p ON f.IdPelícula = p.Id
INNER JOIN Clasificaciones cl ON p.IdClasificación = cl.Id
INNER JOIN Idiomas i ON p.IdIdioma = i.Id
LEFT JOIN PelículaGénero pg ON p.Id = pg.IdPelícula
LEFT JOIN Géneros g ON pg.IdGénero = g.Id
LEFT JOIN Boletos b ON f.Id = b.IdFunción
LEFT JOIN TipoBoletos tb ON b.IdTipoBoleto = tb.Id
LEFT JOIN BoletosCancelados bc ON b.Id = bc.IdBoleto
LEFT JOIN BoletosUsados bu ON b.Id = bu.IdBoleto
LEFT JOIN Usuarios u ON b.IdUsuario = u.Id
LEFT JOIN Asientos a ON b.IdAsiento = a.Id
WHERE f.FechaHora >= @FechaInicio 
    AND f.FechaHora < DATEADD(day, 1, @FechaFin)
    AND f.Activo = 1
    AND (@CineIds IS NULL OR s.IdCine IN (SELECT value FROM STRING_SPLIT(@CineIds, ',')))
    AND (@GeneroIds IS NULL OR g.Id IN (SELECT value FROM STRING_SPLIT(@GeneroIds, ',')))
    AND (@PeliculaIds IS NULL OR p.Id IN (SELECT value FROM STRING_SPLIT(@PeliculaIds, ',')))
    AND (@FuncionIds IS NULL OR f.Id IN (SELECT value FROM STRING_SPLIT(@FuncionIds, ',')))
    AND (@DiasSemana IS NULL OR DATEPART(weekday, f.FechaHora) IN (SELECT value FROM STRING_SPLIT(@DiasSemana, ',')));