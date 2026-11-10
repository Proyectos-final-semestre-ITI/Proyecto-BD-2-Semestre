# Todo lo que se muestra o se pide por consola pasa por acá, para que el
# programa se vea prolijo y parejo. Usa la librería rich (colores, tablas
# y recuadros):  pip install rich

import os

from rich import box
from rich.align import Align
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Console

# Consola de rich que usa todo el programa para mostrar texto con formato.
# highlight=False evita que rich coloree por su cuenta números, correos o
# palabras seguidas de paréntesis; los colores se indican a mano.
consola = Console(highlight=False)

# Nivel del contribuyente con su color, para el encabezado
NIVELES = {"baja": "[green]Bajo[/]", "media": "[yellow]Medio[/]", "alta": "[red]Alto[/]"}


def limpiar_pantalla():
    # En la consola clásica de Windows consola.clear() no borra el contenido,
    # solo mueve el cursor al inicio; por eso se usa cls
    if os.name == "nt":
        os.system("cls")
    else:
        consola.clear()


def encabezado(titulo, usuario=None):
    # Limpia la pantalla y muestra el nombre del programa, quién está
    # conectado y el título de la sección actual
    limpiar_pantalla()
    logo = Text.from_markup(
        "[bold white]PROGRAMA ANTI-ESTAFAS[/]\n[dim]Reporte y consulte números sospechosos[/]",
        justify="center")
    consola.print(Align.center(Panel.fit(logo, border_style="cyan", box=box.DOUBLE, padding=(0, 6))))

    if usuario is not None:
        if usuario["es_admin"]:
            rol = "[bold magenta]Administrador[/]"
        else:
            rol = f"Contribuyente · nivel {NIVELES.get(usuario['nivel'], '-')}"
        consola.print(Align.center(
            f"[dim]Sesión:[/] [bold]{escape(usuario['nombre'])}[/] "
            f"[dim]<{escape(usuario['correo'])}>[/]  [dim]|[/]  {rol}"))

    consola.print()
    consola.rule(f"[bold cyan]{titulo}[/]", style="cyan")
    consola.print()


def menu(opciones, pregunta="Elija una opción"):
    # opciones: lista de (tecla, texto). Devuelve la tecla elegida.
    tabla = Table(box=box.ROUNDED, show_header=False, border_style="cyan", padding=(0, 2))
    tabla.add_column(style="bold cyan", justify="right")
    tabla.add_column()
    for tecla, texto in opciones:
        tabla.add_row(tecla, texto)
    consola.print(tabla)

    teclas = [tecla for tecla, _ in opciones]
    while True:
        opcion = consola.input(f"[bold]{pregunta}:[/] ").strip()
        if opcion in teclas:
            return opcion
        error("Opción inválida, intente de nuevo.")


# --------------------------------------------------------------- Mensajes

def exito(mensaje):
    # Mensaje en verde para una acción que se completó bien
    consola.print(f"[bold black on green] OK [/] {mensaje}")


def error(mensaje):
    # Mensaje en rojo para un dato incorrecto o una falla
    consola.print(f"[bold white on red] ERROR [/] {mensaje}")


def aviso(mensaje):
    # Mensaje en amarillo para advertencias
    consola.print(f"[bold black on yellow] AVISO [/] {mensaje}")


def pausa():
    # Espera a que el usuario presione Enter antes de continuar
    consola.input("\n[dim]Presione Enter para continuar...[/]")


# ------------------------------------------------------ Pedir datos

def pedir_texto(mensaje, maximo, obligatorio=True):
    # Vuelve a preguntar hasta que el dato sea válido. Si no es obligatorio,
    # Enter devuelve "".
    while True:
        dato = consola.input(f"[bold]{mensaje}:[/] ").strip()
        if dato == "" and not obligatorio:
            return ""
        if dato == "":
            error("Este dato es obligatorio.")
        elif len(dato) > maximo:
            error(f"Puede tener como máximo {maximo} caracteres.")
        else:
            return dato


def pedir_numero(mensaje, minimo, maximo=None, obligatorio=True):
    # Devuelve un entero entre minimo y maximo, o None si no es obligatorio
    # y se presiona Enter
    while True:
        dato = pedir_texto(mensaje, 10, obligatorio)
        if dato == "":
            return None
        if not dato.isdigit():
            error("Ingrese un número.")
        elif int(dato) < minimo or (maximo is not None and int(dato) > maximo):
            rango = f"entre {minimo} y {maximo}" if maximo is not None else f"mayor o igual a {minimo}"
            error(f"El número tiene que estar {rango}.")
        else:
            return int(dato)


def confirmar(mensaje):
    # Pregunta de sí o no; devuelve True o False
    while True:
        dato = consola.input(f"[bold]{mensaje}[/] [dim](s/n)[/]: ").strip().lower()
        if dato in ("s", "si", "sí"):
            return True
        if dato in ("n", "no"):
            return False
        error("Responda con s (sí) o n (no).")
