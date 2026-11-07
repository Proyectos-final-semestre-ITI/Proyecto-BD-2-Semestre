# Elegir un país de la tabla Paises (o agregar uno nuevo si no está).
# Se usa al registrarse (país de origen) y al reportar un número.

from rich import box
from rich.markup import escape
from rich.table import Table

import base_datos
import pantalla


def elegir_pais(pregunta):
    # Devuelve un diccionario {"prefijo": ..., "nombre": ...}
    while True:
        lista = base_datos.obtener_paises()

        tabla = Table(box=box.SIMPLE_HEAD, header_style="bold cyan", padding=(0, 2))
        tabla.add_column("N°", justify="right", style="bold cyan")
        tabla.add_column("País")
        tabla.add_column("Prefijo", style="dim")
        for numero, pais in enumerate(lista, start=1):
            tabla.add_row(str(numero), escape(pais["nombre"]), f"+{pais['prefijo']}")
        tabla.add_row("0", "[italic]Otro país (agregar)[/]", "")
        pantalla.consola.print(tabla)

        opcion = pantalla.pedir_numero(pregunta, 0, len(lista))
        if opcion > 0:
            return lista[opcion - 1]

        pais = agregar_pais()
        if pais is not None:
            return pais


def agregar_pais():
    pantalla.consola.print()
    prefijo = pantalla.pedir_texto("Prefijo telefónico del país (ej: 598)", 4).lstrip("+")
    while not (prefijo.isdigit() and 1 <= len(prefijo) <= 3):
        pantalla.error("El prefijo tiene que tener entre 1 y 3 números.")
        prefijo = pantalla.pedir_texto("Prefijo telefónico del país (ej: 598)", 4).lstrip("+")

    existente = base_datos.buscar_pais(prefijo)
    if existente is not None:
        pantalla.aviso(f"El prefijo +{prefijo} ya es de {escape(existente['nombre'])}, se usa ese país.")
        return existente

    nombre = pantalla.pedir_texto("Nombre del país", 20)
    base_datos.guardar_pais(prefijo, nombre)
    pantalla.exito(f"País {escape(nombre)} (+{prefijo}) agregado.")
    return {"prefijo": prefijo, "nombre": nombre}
