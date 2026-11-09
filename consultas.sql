-- ==========================================================
--  Programa Anti-Estafas
--  Consultas SQL utilizadas por el programa (base_datos.py)
-- ==========================================================
--  Los valores que aparecen son de ejemplo. En el programa se
--  envían como parámetros (%s) con los datos que ingresa el usuario.

USE proyectobd;


-- ----------------------------------------------------------
--  1. Usuarios
-- ----------------------------------------------------------

-- 1.1 Búsqueda de usuario por correo (inicio de sesión)
SELECT u.correo, u.nombre, u.paisOrigen AS pais_origen,
       a.correo IS NOT NULL AS es_admin,
       CASE WHEN c.alta THEN 'alta'
            WHEN c.media THEN 'media'
            WHEN c.baja THEN 'baja'
       END AS nivel
FROM Usuarios u
LEFT JOIN Administradores a ON a.correo = u.correo
LEFT JOIN Contribuyentes c ON c.correo = u.correo
WHERE u.correo = 'juan@correo.com';

-- 1.2 Registro de un usuario nuevo
START TRANSACTION;

INSERT INTO Usuarios (correo, nombre, paisOrigen)
VALUES ('juan@correo.com', 'Juan Pérez', 'Uruguay');

INSERT INTO Contribuyentes (correo)
VALUES ('juan@correo.com');

INSERT INTO Acceden (correo, prefijo)
VALUES ('juan@correo.com', '598');

COMMIT;


-- ----------------------------------------------------------
--  2. Países
-- ----------------------------------------------------------

-- 2.1 Listado de países
SELECT prefijo, nombre
FROM Paises
ORDER BY nombre;

-- 2.2 Búsqueda de un país por prefijo
SELECT prefijo, nombre
FROM Paises
WHERE prefijo = '598';

-- 2.3 Alta de un país
INSERT INTO Paises (prefijo, nombre)
VALUES ('372', 'Estonia');


-- ----------------------------------------------------------
--  3. Tipos de estafa
-- ----------------------------------------------------------

-- 3.1 Listado de tipos de estafa con su nivel de riesgo
SELECT ID, nombre, descripcion,
       CASE WHEN alta THEN 'alta' WHEN media THEN 'media' ELSE 'baja' END AS riesgo
FROM Tipos_de_Estafas
ORDER BY ID;


-- ----------------------------------------------------------
--  4. Alta de reportes
-- ----------------------------------------------------------

-- 4.1 Registro de un reporte con sus teléfonos, tipos y evidencias
START TRANSACTION;

INSERT INTO Reportes (descripcion)
VALUES ('Llamaron diciendo ser un familiar y pidieron dinero urgente.');

SET @idr = LAST_INSERT_ID();

INSERT INTO Telefonos_Rep (IDR, num_Tel) VALUES (@idr, '099123456');
INSERT INTO Telefonos_Rep (IDR, num_Tel) VALUES (@idr, '+59898765432');

INSERT INTO Generan (IDR, correo, prefijo)
VALUES (@idr, 'juan@correo.com', '598');

INSERT INTO Contienen (IDR, ID) VALUES (@idr, 1);
INSERT INTO Contienen (IDR, ID) VALUES (@idr, 6);

INSERT INTO Evidencias (IDR, descripcion) VALUES (@idr, 'Captura de la conversación');
INSERT INTO Evidencias (IDR, descripcion) VALUES (@idr, 'Texto del SMS recibido');

COMMIT;


-- ----------------------------------------------------------
--  5. Consulta de reportes
-- ----------------------------------------------------------

-- 5.1 Listado de todos los reportes
SELECT r.IDR, r.descripcion, r.fecha, r.hora,
       g.correo AS correo_usuario, u.nombre AS nombre_usuario,
       p.prefijo, p.nombre AS pais,
       GROUP_CONCAT(DISTINCT t.num_Tel ORDER BY t.num_Tel SEPARATOR ', ') AS telefonos,
       GROUP_CONCAT(DISTINCT te.nombre ORDER BY te.nombre SEPARATOR ', ') AS tipos,
       a.prioridad, a.cancelado, a.confirmado
FROM Reportes r
LEFT JOIN Generan g ON g.IDR = r.IDR
LEFT JOIN Usuarios u ON u.correo = g.correo
LEFT JOIN Paises p ON p.prefijo = g.prefijo
LEFT JOIN Telefonos_Rep t ON t.IDR = r.IDR
LEFT JOIN Contienen c ON c.IDR = r.IDR
LEFT JOIN Tipos_de_Estafas te ON te.ID = c.ID
LEFT JOIN Aceptan a ON a.IDR = r.IDR
GROUP BY r.IDR
ORDER BY r.IDR DESC;

-- 5.2 Búsqueda de reportes por número de teléfono
-- Se ignoran el "+" y los ceros iniciales, de modo que 099123456,
-- 99123456 y +59899123456 encuentran el mismo número.
SELECT r.IDR, r.descripcion, r.fecha, r.hora,
       g.correo AS correo_usuario, u.nombre AS nombre_usuario,
       p.prefijo, p.nombre AS pais,
       GROUP_CONCAT(DISTINCT t.num_Tel ORDER BY t.num_Tel SEPARATOR ', ') AS telefonos,
       GROUP_CONCAT(DISTINCT te.nombre ORDER BY te.nombre SEPARATOR ', ') AS tipos,
       a.prioridad, a.cancelado, a.confirmado
FROM Reportes r
LEFT JOIN Generan g ON g.IDR = r.IDR
LEFT JOIN Usuarios u ON u.correo = g.correo
LEFT JOIN Paises p ON p.prefijo = g.prefijo
LEFT JOIN Telefonos_Rep t ON t.IDR = r.IDR
LEFT JOIN Contienen c ON c.IDR = r.IDR
LEFT JOIN Tipos_de_Estafas te ON te.ID = c.ID
LEFT JOIN Aceptan a ON a.IDR = r.IDR
WHERE r.IDR IN (
    SELECT IDR FROM Telefonos_Rep
    WHERE TRIM(LEADING '0' FROM REPLACE(num_Tel, '+', '')) LIKE '%99123456%'
       OR LOCATE(TRIM(LEADING '0' FROM REPLACE(num_Tel, '+', '')), '99123456') > 0)
GROUP BY r.IDR
ORDER BY r.IDR DESC;

-- 5.3 Reportes pendientes de revisión (sin revisar o marcados como pendientes)
SELECT r.IDR, r.descripcion, r.fecha, r.hora,
       g.correo AS correo_usuario, u.nombre AS nombre_usuario,
       p.prefijo, p.nombre AS pais,
       GROUP_CONCAT(DISTINCT t.num_Tel ORDER BY t.num_Tel SEPARATOR ', ') AS telefonos,
       GROUP_CONCAT(DISTINCT te.nombre ORDER BY te.nombre SEPARATOR ', ') AS tipos,
       a.prioridad, a.cancelado, a.confirmado
FROM Reportes r
LEFT JOIN Generan g ON g.IDR = r.IDR
LEFT JOIN Usuarios u ON u.correo = g.correo
LEFT JOIN Paises p ON p.prefijo = g.prefijo
LEFT JOIN Telefonos_Rep t ON t.IDR = r.IDR
LEFT JOIN Contienen c ON c.IDR = r.IDR
LEFT JOIN Tipos_de_Estafas te ON te.ID = c.ID
LEFT JOIN Aceptan a ON a.IDR = r.IDR
WHERE a.IDR IS NULL OR a.pendiente = 1
GROUP BY r.IDR
ORDER BY r.IDR DESC;

-- 5.4 Evidencias de un reporte
SELECT descripcion
FROM Evidencias
WHERE IDR = 1
ORDER BY IDE;


-- ----------------------------------------------------------
--  6. Revisión de reportes (administradores)
-- ----------------------------------------------------------

-- 6.1 Registro o actualización de la revisión de un reporte
-- (requiere MySQL 8.0.19 o superior)
INSERT INTO Aceptan (IDR, correo, prioridad, cancelado, pendiente, confirmado)
VALUES (1, 'admin@correo.com', 3, FALSE, FALSE, TRUE) AS nuevo
ON DUPLICATE KEY UPDATE correo = nuevo.correo, prioridad = nuevo.prioridad,
    cancelado = nuevo.cancelado, pendiente = nuevo.pendiente,
    confirmado = nuevo.confirmado;
