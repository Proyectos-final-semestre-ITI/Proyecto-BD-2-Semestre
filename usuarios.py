# Todo lo que tiene que ver con los usuarios.
# El "inicio de sesión" no pide contraseña: alcanza con el correo. Si el
# correo no está en la base, se registra al usuario como Contribuyente.

from rich.markup import escape

import base_datos
import pantalla
import paises


def pedir_correo():
    correo = pantalla.pedir_texto("Correo", 50).lower()
    while "@" not in correo or "." not in correo.split("@")[-1]:
        pantalla.error("El correo no es válido.")
        correo = pantalla.pedir_texto("Correo", 50).lower()
    return correo


def iniciar_sesion():
    pantalla.encabezado("Iniciar sesión")
    pantalla.consola.print("[dim]Ingrese su correo. Si es la primera vez, se le pedirán algunos datos más.[/]\n")
    correo = pedir_correo()

    usuario = base_datos.buscar_usuario(correo)
    if usuario is not None:
        return usuario

    pantalla.consola.print()
    pantalla.aviso("Es la primera vez que ingresa con este correo. Complete sus datos para registrarse.")
    pantalla.consola.print()
    nombre = pantalla.pedir_texto("Nombre", 100)
    pantalla.consola.print()
    pais = paises.elegir_pais("¿Cuál es su país de origen? (N°)")

    usuario = {
        "correo": correo,
        "nombre": nombre,
        "pais_origen": pais["nombre"],
    }
    base_datos.guardar_usuario(usuario, pais["prefijo"])

    pantalla.consola.print()
    pantalla.exito(f"¡Bienvenido, {escape(nombre)}! Ya está registrado.")
    pantalla.pausa()
    # Se vuelve a leer de la base para tener también el rol y el nivel
    return base_datos.buscar_usuario(correo)
