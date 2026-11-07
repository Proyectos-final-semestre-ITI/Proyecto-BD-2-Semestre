USE proyectobd;

CREATE TABLE Usuarios(
    correo VARCHAR(50) not null,
    nombre VARCHAR(100) not null,
    paisOrigen VARCHAR(20) not null,
    CONSTRAINT CLP_Usuarios PRIMARY KEY(correo));

CREATE TABLE Paises(
    prefijo CHAR(3) not null,
    nombre VARCHAR(20) not null,
    CONSTRAINT CLP_Paises PRIMARY KEY(prefijo));

CREATE TABLE Acceden(
    correo VARCHAR(50) not null,
    prefijo CHAR(3) not null,
    CONSTRAINT CLP_Acceden PRIMARY KEY(correo, prefijo),
    CONSTRAINT CLF_Acceden_Usuarios FOREIGN KEY(correo) REFERENCES Usuarios(correo) on DELETE CASCADE,
    CONSTRAINT CLF_Acceden_Paises FOREIGN KEY(prefijo) REFERENCES Paises(prefijo) on DELETE CASCADE);

CREATE TABLE Contribuyentes(
    correo VARCHAR(50) not null,
    baja BOOLEAN not null DEFAULT true,
    media BOOLEAN not null DEFAULT false,
    alta BOOLEAN not null DEFAULT false,
    CONSTRAINT CLP_Contribuyentes PRIMARY KEY(correo),
    CONSTRAINT CLF_Contribuyentes FOREIGN KEY(correo) REFERENCES Usuarios(correo) on DELETE CASCADE);

CREATE TABLE Administradores(
    correo VARCHAR(50) not null,
    CONSTRAINT CLP_Administradores PRIMARY KEY(correo),
    CONSTRAINT CLF_Administradores FOREIGN KEY(correo) REFERENCES Usuarios(correo) on DELETE CASCADE);

CREATE TABLE Reportes(
    IDR int not null AUTO_INCREMENT,
    descripcion TEXT not null,
    hora TIME not null DEFAULT(current_time),
    fecha DATE not null DEFAULT(current_date),
    CONSTRAINT CLP_Reportes PRIMARY KEY(IDR));

CREATE TABLE Telefonos_Rep(
    IDR int not null,
    num_Tel VARCHAR(14) not null,
    CONSTRAINT CLP_Telefonos_Rep PRIMARY KEY(IDR, num_Tel),
    CONSTRAINT CLF_Telefonos_Rep FOREIGN KEY(IDR) REFERENCES Reportes(IDR) on DELETE CASCADE);

CREATE TABLE Generan(
    IDR int not null,
    correo VARCHAR(50) not null,
    prefijo CHAR(3) not null,
    CONSTRAINT CLP_Generan PRIMARY KEY(IDR),
    CONSTRAINT CLF_Generan_Reportes FOREIGN KEY(IDR) REFERENCES Reportes(IDR) on DELETE CASCADE,
    CONSTRAINT CLF_Generan_Usuarios FOREIGN KEY(correo) REFERENCES Usuarios(correo) on DELETE CASCADE,
    CONSTRAINT CLF_Generan_Paises FOREIGN KEY(prefijo) REFERENCES Paises(prefijo) on DELETE CASCADE);

CREATE TABLE Aceptan(
    IDR int not null,
    correo VARCHAR(50) not null,
    prioridad TINYINT NOT NULL DEFAULT 1,
    cancelado BOOLEAN NOT NULL DEFAULT FALSE,
    pendiente BOOLEAN NOT NULL DEFAULT TRUE,
    confirmado BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT CLP_Aceptan PRIMARY KEY(IDR),
    CONSTRAINT CLF_Aceptan_Reportes FOREIGN KEY(IDR) REFERENCES Reportes(IDR) on DELETE CASCADE,
    CONSTRAINT CLF_Aceptan_Administradores FOREIGN KEY(correo) REFERENCES Administradores(correo) ON DELETE CASCADE,
    CONSTRAINT CK_Aceptan_Prioridad CHECK (prioridad BETWEEN 1 AND 3));

CREATE TABLE Evidencias(
    IDR int not null,
    IDE int not null AUTO_INCREMENT,
    descripcion TEXT not null,
    CONSTRAINT CLP_Evidencias PRIMARY KEY(IDR, IDE),
    INDEX IDX_Evidencias_IDE (IDE),
    CONSTRAINT CLF_Evidencias FOREIGN KEY(IDR) REFERENCES Reportes(IDR) on DELETE CASCADE);

CREATE TABLE Tipos_de_Estafas(
    ID int not null AUTO_INCREMENT,
    descripcion TEXT not null,
    nombre VARCHAR(30) not null,
    baja BOOLEAN not null,
    media BOOLEAN not null,
    alta BOOLEAN not null,
    CONSTRAINT CLP_Tip_Estafas PRIMARY KEY(ID));

CREATE TABLE Contienen(
    IDR int not null,
    ID int not null,
    CONSTRAINT CLP_Contienen PRIMARY KEY(IDR, ID),
    CONSTRAINT CLF_Contienen_Reportes FOREIGN KEY(IDR) REFERENCES Reportes(IDR) on DELETE CASCADE,
    CONSTRAINT CLF_Contienen_Tipos FOREIGN KEY(ID) REFERENCES Tipos_de_Estafas(ID) on DELETE CASCADE);
