# Menú principal del programa. Ejecutar con:  python menu.py
# Necesita el servidor MySQL encendido y la base proyectobd creada
# (proyectobd.sql y datos_iniciales.sql).

import librerias

librerias.verificar()

from rich import box
from rich.markup import escape
from rich.panel import Panel

import administracion
import base_datos
import estafadores
import pantalla
import usuarios


def opciones_menu(usuario):
    opciones = [
        ("1", "Reportar un número"),
        ("2", "Buscar un número"),
        ("3", "Ver todos los reportes"),
    ]
    if usuario["es_admin"]:
        opciones.append(("4", "[magenta]Revisar reportes pendientes[/]"))
    opciones += [
        ("9", "Cerrar sesión"),
        ("0", "Salir"),
    ]
    return opciones


def error_de_conexion(error):
    pantalla.encabezado("Sin conexión")
    pantalla.consola.print(Panel(
        "No se pudo conectar a la base de datos MySQL.\n\n"
        f"[dim]{escape(str(error))}[/]\n\n"
        "Revise que:\n"
        "  • el servidor MySQL esté iniciado (acceso directo [bold]Iniciar MySQL[/])\n"
        f"  • exista la base [bold]{base_datos.CONFIG['database']}[/] (script proyectobd.sql)\n"
        f"  • el usuario [bold]{base_datos.CONFIG['user']}[/] y la contraseña sean correctos "
        "(variables BD_USUARIO y BD_CLAVE)",
        title="[bold]Error de conexión[/]", border_style="red", box=box.ROUNDED, padding=(1, 2)))


def main():
    try:
        base_datos.conectar()
    except base_datos.ErrorBD as error:
        error_de_conexion(error)
        pantalla.pausa()
        return

    usuario = usuarios.iniciar_sesion()

    while True:
        pantalla.encabezado("Menú principal", usuario)
        opcion = pantalla.menu(opciones_menu(usuario))

        try:
            if opcion == "1":
                estafadores.agregar_estafador(usuario)
            elif opcion == "2":
                estafadores.buscar_numero(usuario)
            elif opcion == "3":
                estafadores.ver_estafadores(usuario)
            elif opcion == "4":
                administracion.revisar_reportes(usuario)
            elif opcion == "9":
                usuario = usuarios.iniciar_sesion()
            elif opcion == "0":
                break
        except base_datos.ErrorBD as error:
            pantalla.consola.print()
            pantalla.error(f"Error de la base de datos: {escape(str(error))}")
            pantalla.pausa()

    base_datos.desconectar()
    pantalla.consola.print(f"\n[cyan]Hasta luego, {escape(usuario['nombre'])}.[/]\n")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C: salir sin mostrar el error de Python
        pantalla.consola.print("\n[cyan]Programa cerrado.[/]\n")
