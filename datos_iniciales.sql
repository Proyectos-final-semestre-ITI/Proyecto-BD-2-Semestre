-- Datos iniciales: países, tipos de estafa y datos de ejemplo
-- (cada tabla queda con al menos 5 tuplas).
USE proyectobd;

INSERT IGNORE INTO Paises (prefijo, nombre) VALUES
    ('598', 'Uruguay'),
    ('54', 'Argentina'),
    ('55', 'Brasil'),
    ('56', 'Chile'),
    ('595', 'Paraguay'),
    ('591', 'Bolivia'),
    ('51', 'Perú'),
    ('57', 'Colombia'),
    ('58', 'Venezuela'),
    ('593', 'Ecuador'),
    ('52', 'México'),
    ('34', 'España'),
    ('1', 'Estados Unidos');

INSERT IGNORE INTO Tipos_de_Estafas (ID, nombre, descripcion, baja, media, alta) VALUES
    (1, 'Falso familiar', 'Se hacen pasar por un familiar en apuros y piden dinero urgente.', false, false, true),
    (2, 'Falso banco', 'Dicen ser del banco y piden claves, códigos o datos de la tarjeta.', false, false, true),
    (3, 'Inversión falsa', 'Prometen ganancias rápidas con inversiones o criptomonedas.', false, false, true),
    (4, 'Premio o sorteo falso', 'Avisan de un premio y piden pagar o dar datos para cobrarlo.', false, true, false),
    (5, 'Venta online falsa', 'Venden algo que nunca llega o piden una seña por adelantado.', false, true, false),
    (6, 'Phishing por mensaje', 'Mandan links por SMS o WhatsApp para robar datos o cuentas.', false, true, false),
    (7, 'Falso soporte técnico', 'Dicen ser de una empresa y piden acceso remoto o pagos.', false, true, false),
    (8, 'Llamada spam', 'Llamadas insistentes, publicidad engañosa o encuestas falsas.', true, false, false);


-- ------------------------------------------------------------
--  Usuarios
-- ------------------------------------------------------------

INSERT IGNORE INTO Usuarios (correo, nombre, paisOrigen) VALUES
    ('lucia.fernandez@correo.com', 'Lucía Fernández', 'Uruguay'),
    ('martin.rodriguez@correo.com', 'Martín Rodríguez', 'Uruguay'),
    ('camila.silva@correo.com', 'Camila Silva', 'Brasil'),
    ('diego.gonzalez@correo.com', 'Diego González', 'Argentina'),
    ('valentina.perez@correo.com', 'Valentina Pérez', 'Chile'),
    ('sofia.martinez@correo.com', 'Sofía Martínez', 'Uruguay'),
    ('nicolas.suarez@correo.com', 'Nicolás Suárez', 'Uruguay'),
    ('florencia.lopez@correo.com', 'Florencia López', 'Argentina'),
    ('joaquin.castro@correo.com', 'Joaquín Castro', 'Paraguay'),
    ('agustina.romero@correo.com', 'Agustina Romero', 'España');

INSERT IGNORE INTO Contribuyentes (correo, baja, media, alta) VALUES
    ('lucia.fernandez@correo.com', false, false, true),
    ('martin.rodriguez@correo.com', false, true, false),
    ('camila.silva@correo.com', true, false, false),
    ('diego.gonzalez@correo.com', false, true, false),
    ('valentina.perez@correo.com', true, false, false);

INSERT IGNORE INTO Administradores (correo) VALUES
    ('sofia.martinez@correo.com'),
    ('nicolas.suarez@correo.com'),
    ('florencia.lopez@correo.com'),
    ('joaquin.castro@correo.com'),
    ('agustina.romero@correo.com');

INSERT IGNORE INTO Acceden (correo, prefijo) VALUES
    ('lucia.fernandez@correo.com', '598'),
    ('martin.rodriguez@correo.com', '598'),
    ('martin.rodriguez@correo.com', '54'),
    ('camila.silva@correo.com', '55'),
    ('diego.gonzalez@correo.com', '54'),
    ('valentina.perez@correo.com', '56'),
    ('sofia.martinez@correo.com', '598'),
    ('nicolas.suarez@correo.com', '598'),
    ('florencia.lopez@correo.com', '54'),
    ('joaquin.castro@correo.com', '595'),
    ('agustina.romero@correo.com', '34');


-- ------------------------------------------------------------
--  Reportes
-- ------------------------------------------------------------

INSERT IGNORE INTO Reportes (IDR, descripcion, hora, fecha) VALUES
    (2, 'Llamaron haciéndose pasar por mi nieto. Dijo que había tenido un accidente y necesitaba dinero para el abogado.', '10:15:00', '2026-10-02'),
    (3, 'Recibí un SMS del supuesto banco con un link para "desbloquear" la tarjeta. La página pedía usuario y clave.', '18:40:00', '2026-10-06'),
    (4, 'Me escribieron por WhatsApp diciendo que gané un sorteo de un supermercado. Para cobrar pedían pagar el envío.', '13:05:00', '2026-10-11'),
    (5, 'Ofrecían una inversión en criptomonedas con ganancias del 30% mensual. Pidieron una transferencia inicial.', '21:20:00', '2026-10-17'),
    (6, 'Llamada de un supuesto técnico de Microsoft que pedía instalar un programa de acceso remoto.', '09:50:00', '2026-10-23');

INSERT IGNORE INTO Telefonos_Rep (IDR, num_Tel) VALUES
    (2, '099456123'),
    (2, '098112233'),
    (3, '091234567'),
    (4, '+5511987654321'),
    (5, '1145678901'),
    (5, '1167890123'),
    (6, '+56912345678');

INSERT IGNORE INTO Generan (IDR, correo, prefijo) VALUES
    (2, 'lucia.fernandez@correo.com', '598'),
    (3, 'martin.rodriguez@correo.com', '598'),
    (4, 'camila.silva@correo.com', '55'),
    (5, 'diego.gonzalez@correo.com', '54'),
    (6, 'valentina.perez@correo.com', '56');

INSERT IGNORE INTO Contienen (IDR, ID) VALUES
    (2, 1),
    (3, 2),
    (3, 6),
    (4, 4),
    (5, 3),
    (6, 7);

INSERT IGNORE INTO Evidencias (IDR, IDE, descripcion) VALUES
    (2, 1, 'Grabación de la llamada'),
    (3, 2, 'Captura del SMS recibido'),
    (3, 3, 'Link del mensaje: http://banco-seguro-uy.com/desbloqueo'),
    (4, 4, 'Captura de la conversación de WhatsApp'),
    (5, 5, 'Comprobante de la transferencia solicitada'),
    (6, 6, 'Nombre del programa que pedían instalar: AnyDesk');


-- ------------------------------------------------------------
--  Revisiones de los administradores
-- ------------------------------------------------------------

INSERT IGNORE INTO Aceptan (IDR, correo, prioridad, cancelado, pendiente, confirmado) VALUES
    (2, 'sofia.martinez@correo.com', 3, false, false, true),
    (3, 'nicolas.suarez@correo.com', 3, false, false, true),
    (4, 'florencia.lopez@correo.com', 2, false, true, false),
    (5, 'joaquin.castro@correo.com', 3, false, false, true),
    (6, 'agustina.romero@correo.com', 1, true, false, false);
