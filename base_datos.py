# Conexión con la base de datos MySQL (proyectobd) y todas las consultas.
import os

import mysql.connector
from mysql.connector import Error as ErrorBD

# Datos de conexión. Se pueden cambiar con variables de entorno, sin
# modificar el código (BD_HOST, BD_PUERTO, BD_USUARIO, BD_CLAVE, BD_NOMBRE).
CONFIG = {
    "host": os.getenv("BD_HOST", "127.0.0.1"),
    "port": int(os.getenv("BD_PUERTO", "3306")),
    "user": os.getenv("BD_USUARIO", "root"),
    "password": os.getenv("BD_CLAVE", ""),
    "database": os.getenv("BD_NOMBRE", "proyectobd"),
    "autocommit": True,
}

# Se mantiene una única conexión abierta durante todo el programa
conexion = None


def conectar():
    # Abre la conexión si todavía no existe o si se cortó
    global conexion
    if conexion is None or not conexion.is_connected():
        conexion = mysql.connector.connect(**CONFIG)
    return conexion


def desconectar():
    # Cierra la conexión al salir del programa
    if conexion is not None and conexion.is_connected():
        conexion.close()


def consultar(sql, parametros=()):
    # Ejecuta un SELECT y devuelve las filas como diccionarios {columna: valor}.
    # Los datos se pasan aparte, en parametros (%s), para evitar inyección SQL.
    cursor = conectar().cursor(dictionary=True)
    cursor.execute(sql, parametros)
    filas = cursor.fetchall()
    cursor.close()
    return filas


def ejecutar(sql, parametros=()):
    # Ejecuta un INSERT o UPDATE simple; con autocommit queda guardado al instante
    cursor = conectar().cursor()
    cursor.execute(sql, parametros)
    cursor.close()


# ----------------------------------------------------------------- Usuarios

def buscar_usuario(correo):
    # Devuelve los datos del usuario, si es administrador y su nivel como
    # contribuyente; None si el correo no está registrado
    filas = consultar("""
        SELECT u.correo, u.nombre, u.paisOrigen AS pais_origen,
               a.correo IS NOT NULL AS es_admin,
               CASE WHEN c.alta THEN 'alta'
                    WHEN c.media THEN 'media'
                    WHEN c.baja THEN 'baja'
               END AS nivel
        FROM Usuarios u
        LEFT JOIN Administradores a ON a.correo = u.correo
        LEFT JOIN Contribuyentes c ON c.correo = u.correo
        WHERE u.correo = %s
    """, (correo,))
    return filas[0] if filas else None


def guardar_usuario(usuario, prefijo_pais):
    # Registra un usuario nuevo como contribuyente con acceso a su país.
    # Los tres INSERT forman una transacción: si uno falla, no se guarda ninguno.
    con = conectar()
    cursor = con.cursor()
    try:
        con.start_transaction()
        cursor.execute(
            "INSERT INTO Usuarios (correo, nombre, paisOrigen) VALUES (%s, %s, %s)",
            (usuario["correo"], usuario["nombre"], usuario["pais_origen"]))
        cursor.execute("INSERT INTO Contribuyentes (correo) VALUES (%s)", (usuario["correo"],))
        cursor.execute("INSERT INTO Acceden (correo, prefijo) VALUES (%s, %s)",
                       (usuario["correo"], prefijo_pais))
        con.commit()
    except ErrorBD:
        con.rollback()
        raise
    finally:
        cursor.close()


# ------------------------------------------------------- Países y tipos

def obtener_paises():
    # Lista de países ordenada por nombre
    return consultar("SELECT prefijo, nombre FROM Paises ORDER BY nombre")


def buscar_pais(prefijo):
    # Devuelve el país con ese prefijo, o None si no existe
    filas = consultar("SELECT prefijo, nombre FROM Paises WHERE prefijo = %s", (prefijo,))
    return filas[0] if filas else None


def guardar_pais(prefijo, nombre):
    # Agrega un país nuevo a la tabla Paises
    ejecutar("INSERT INTO Paises (prefijo, nombre) VALUES (%s, %s)", (prefijo, nombre))


def obtener_tipos_estafa():
    # Lista de tipos de estafa; las columnas alta, media y baja se resumen
    # en una sola (riesgo)
    return consultar("""
        SELECT ID, nombre, descripcion,
               CASE WHEN alta THEN 'alta' WHEN media THEN 'media' ELSE 'baja' END AS riesgo
        FROM Tipos_de_Estafas
        ORDER BY ID
    """)


# ----------------------------------------------------------------- Reportes

def guardar_reporte(reporte):
    # Guarda el reporte junto con sus teléfonos, quién lo generó, sus tipos de
    # estafa y sus evidencias, todo en una transacción. Devuelve el N° (IDR).
    con = conectar()
    cursor = con.cursor()
    try:
        con.start_transaction()
        cursor.execute("INSERT INTO Reportes (descripcion) VALUES (%s)", (reporte["descripcion"],))
        idr = cursor.lastrowid

        for telefono in reporte["telefonos"]:
            cursor.execute("INSERT INTO Telefonos_Rep (IDR, num_Tel) VALUES (%s, %s)",
                           (idr, telefono))
        cursor.execute("INSERT INTO Generan (IDR, correo, prefijo) VALUES (%s, %s, %s)",
                       (idr, reporte["correo_usuario"], reporte["prefijo"]))
        for id_tipo in reporte["tipos"]:
            cursor.execute("INSERT INTO Contienen (IDR, ID) VALUES (%s, %s)", (idr, id_tipo))
        for evidencia in reporte["evidencias"]:
            cursor.execute("INSERT INTO Evidencias (IDR, descripcion) VALUES (%s, %s)",
                           (idr, evidencia))
        con.commit()
        return idr
    except ErrorBD:
        con.rollback()
        raise
    finally:
        cursor.close()


# Consulta base de los reportes: una fila por reporte, con sus teléfonos y
# tipos de estafa unidos en un texto. En {filtro} va el WHERE de cada búsqueda.
CONSULTA_REPORTES = """
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
    {filtro}
    GROUP BY r.IDR
    ORDER BY r.IDR DESC
"""


def obtener_reportes(telefono=None, solo_pendientes=False):
    # Devuelve todos los reportes, los de un teléfono o solo los pendientes de
    # revisión. Al buscar un teléfono se ignoran el "+" y los ceros iniciales,
    # de modo que 099123456 y +59899123456 se consideran el mismo número.
    filtro, parametros = "", ()

    if telefono is not None:
        buscado = telefono.lstrip("+").lstrip("0") or telefono
        filtro = """
            WHERE r.IDR IN (
                SELECT IDR FROM Telefonos_Rep
                WHERE TRIM(LEADING '0' FROM REPLACE(num_Tel, '+', '')) LIKE %s
                   OR LOCATE(TRIM(LEADING '0' FROM REPLACE(num_Tel, '+', '')), %s) > 0)
        """
        parametros = (f"%{buscado}%", buscado)
    elif solo_pendientes:
        filtro = "WHERE a.IDR IS NULL OR a.pendiente = 1"

    return consultar(CONSULTA_REPORTES.format(filtro=filtro), parametros)


def obtener_evidencias(idr):
    # Lista con el texto de cada evidencia del reporte
    filas = consultar("SELECT descripcion FROM Evidencias WHERE IDR = %s ORDER BY IDE", (idr,))
    return [fila["descripcion"] for fila in filas]


def guardar_revision(idr, correo_admin, prioridad, estado):
    # Guarda la revisión de un administrador. Si el reporte ya tenía una, se
    # actualiza en lugar de crear otra (ON DUPLICATE KEY UPDATE).
    ejecutar("""
        INSERT INTO Aceptan (IDR, correo, prioridad, cancelado, pendiente, confirmado)
        VALUES (%s, %s, %s, %s, %s, %s) AS nuevo
        ON DUPLICATE KEY UPDATE correo = nuevo.correo, prioridad = nuevo.prioridad,
            cancelado = nuevo.cancelado, pendiente = nuevo.pendiente,
            confirmado = nuevo.confirmado
    """, (idr, correo_admin, prioridad,
          estado == "cancelado", estado == "pendiente", estado == "confirmado"))
