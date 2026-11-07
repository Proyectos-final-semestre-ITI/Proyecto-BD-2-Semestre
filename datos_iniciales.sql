-- Datos iniciales: países y tipos de estafa para elegir desde el programa.
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
