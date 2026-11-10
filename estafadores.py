# Todo lo que tiene que ver con los estafadores: reportar un número,
# buscarlo y ver los reportes guardados en la base.

from rich import box
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

import base_datos
import pantalla
import paises

# Textos con color para el riesgo de cada tipo de estafa y la prioridad
# que asigna un administrador a un reporte
RIESGOS = {"baja": "[green]Bajo[/]", "media": "[yellow]Medio[/]", "alta": "[red]Alto[/]"}
PRIORIDADES = {1: "[green]Baja[/]", 2: "[yellow]Media[/]", 3: "[red]Alta[/]"}


# --------------------------------------------------------------- Teléfonos

def normalizar_telefono(texto):
    # Saca espacios, guiones y paréntesis: "+598 (99) 123-456" -> "+59899123456"
    return "".join(c for c in texto if c.isdigit() or c == "+")


def pedir_telefono(mensaje):
    # Pide un teléfono hasta que sea válido: de 6 a 14 caracteres, solo
    # números y un "+" opcional al principio
    while True:
        numero = normalizar_telefono(pantalla.pedir_texto(mensaje, 30))
        digitos = numero[1:] if numero.startswith("+") else numero
        if digitos.isdigit() and 6 <= len(numero) <= 14:
            return numero
        pantalla.error("Ingrese un teléfono válido (entre 6 y 14 números, puede empezar con +).")


# ------------------------------------------------------- Mostrar reportes

def estado(reporte):
    # Estado del reporte con su color. Un reporte sin revisar figura como pendiente.
    if reporte["confirmado"]:
        return "[bold red]Estafa confirmada[/]"
    if reporte["cancelado"]:
        return "[dim]Descartado[/]"
    return "[yellow]Pendiente[/]"


def fecha_hora(reporte):
    # Fecha y hora del reporte en formato dd/mm/aaaa hh:mm.
    # La hora llega como timedelta (así devuelve MySQL las columnas TIME)
    minutos = int(reporte["hora"].total_seconds()) // 60
    return f"{reporte['fecha']:%d/%m/%Y} {minutos // 60:02d}:{minutos % 60:02d}"


def recortar(texto, largo):
    # Acorta un texto largo y le agrega puntos suspensivos
    return texto if len(texto) <= largo else texto[:largo - 1] + "…"


def mostrar_tabla(reportes):
    # Muestra una lista de reportes en forma de tabla.
    # La descripción completa se ve en el detalle; en la tabla va recortada
    # y solo si la consola es ancha
    con_descripcion = pantalla.consola.width >= 100

    tabla = Table(box=box.ROUNDED, header_style="bold cyan", border_style="bright_black",
                  row_styles=["", "on grey11"])
    tabla.add_column("N°", justify="right", style="bold", no_wrap=True)
    tabla.add_column("Fecha", no_wrap=True)
    tabla.add_column("Teléfono(s)", style="bold", no_wrap=True)
    tabla.add_column("País")
    tabla.add_column("Tipo de estafa")
    if con_descripcion:
        tabla.add_column("Descripción")
    tabla.add_column("Estado", no_wrap=True)

    for reporte in reportes:
        fila = [
            str(reporte["IDR"]),
            f"{reporte['fecha']:%d/%m/%Y}",
            escape((reporte["telefonos"] or "-").replace(", ", "\n")),
            escape(reporte["pais"] or "-"),
            escape((reporte["tipos"] or "-").replace(", ", "\n")),
        ]
        if con_descripcion:
            fila.append(escape(recortar(reporte["descripcion"], 30)))
        fila.append(estado(reporte))
        tabla.add_row(*fila)
    pantalla.consola.print(tabla)


def mostrar_detalle(reporte):
    # Muestra todos los datos de un reporte, incluidas sus evidencias, dentro
    # de un recuadro cuyo color depende del estado
    datos = Table.grid(padding=(0, 2))
    datos.add_column(style="bold cyan", justify="right")
    datos.add_column()
    datos.add_row("Fecha", fecha_hora(reporte))
    datos.add_row("Teléfono(s)", f"[bold]{escape(reporte['telefonos'] or '-')}[/]")
    if reporte["prefijo"] is not None:
        datos.add_row("País", f"{escape(reporte['pais'])} [dim](+{reporte['prefijo']})[/]")
    else:
        datos.add_row("País", "-")
    datos.add_row("Tipo de estafa", escape(reporte["tipos"] or "Sin especificar"))
    datos.add_row("Estado", estado(reporte))
    if reporte["prioridad"] is not None:
        datos.add_row("Prioridad", PRIORIDADES[reporte["prioridad"]])
    datos.add_row("Reportado por", f"{escape(reporte['nombre_usuario'] or '-')} "
                                   f"[dim]<{escape(reporte['correo_usuario'] or '-')}>[/]")
    datos.add_row("", "")
    datos.add_row("Descripción", escape(reporte["descripcion"]))

    evidencias = base_datos.obtener_evidencias(reporte["IDR"])
    if evidencias:
        datos.add_row("", "")
        datos.add_row("Evidencias", "\n".join(f"• {escape(e)}" for e in evidencias))

    if reporte["confirmado"]:
        color = "red"
    elif reporte["cancelado"]:
        color = "bright_black"
    else:
        color = "yellow"
    pantalla.consola.print(Panel(datos, title=f"[bold]Reporte N° {reporte['IDR']}[/]",
                                 title_align="left", border_style=color, box=box.ROUNDED,
                                 padding=(1, 2)))


def ver_detalle(reportes, usuario, titulo):
    # Pide el N° de un reporte de la lista y lo muestra completo.
    # Devuelve False cuando el usuario presiona Enter para volver.
    idr = pantalla.pedir_numero("\nN° de reporte para ver el detalle (Enter para volver)",
                                1, obligatorio=False)
    if idr is None:
        return False

    reporte = next((r for r in reportes if r["IDR"] == idr), None)
    if reporte is None:
        pantalla.error("Ese reporte no está en la lista.")
        pantalla.pausa()
        return True

    pantalla.encabezado(titulo, usuario)
    mostrar_detalle(reporte)
    pantalla.pausa()
    return True


# --------------------------------------------------------------- Reportar

def elegir_tipos():
    # Muestra los tipos de estafa y permite elegir uno o varios, separados por
    # coma. Es opcional: devuelve la lista de ID elegidos, que puede estar vacía.
    tipos = base_datos.obtener_tipos_estafa()
    if not tipos:
        return []

    tabla = Table(box=box.SIMPLE_HEAD, header_style="bold cyan", padding=(0, 2))
    tabla.add_column("N°", justify="right", style="bold cyan")
    tabla.add_column("Tipo de estafa", style="bold")
    tabla.add_column("Riesgo")
    tabla.add_column("De qué se trata", style="dim")
    for tipo in tipos:
        tabla.add_row(str(tipo["ID"]), escape(tipo["nombre"]), RIESGOS[tipo["riesgo"]],
                      escape(tipo["descripcion"]))
    pantalla.consola.print(tabla)

    ids_validos = {tipo["ID"] for tipo in tipos}
    while True:
        texto = pantalla.pedir_texto("Tipo(s) de estafa (N° separados por coma, Enter si no sabe)",
                                     50, obligatorio=False)
        if texto == "":
            return []
        partes = [parte.strip() for parte in texto.split(",") if parte.strip()]
        if all(parte.isdigit() and int(parte) in ids_validos for parte in partes):
            return sorted({int(parte) for parte in partes})
        pantalla.error("Alguno de los números no está en la lista.")


def agregar_estafador(usuario):
    # Opción 1 del menú. Pide los datos del número sospechoso, muestra un
    # resumen y guarda el reporte si el usuario lo confirma.
    pantalla.encabezado("Reportar un número", usuario)
    pantalla.consola.print("[dim]Complete los datos del número sospechoso. "
                           "Los datos opcionales se pueden saltear con Enter.[/]\n")

    telefonos = [pedir_telefono("Número de teléfono")]
    anteriores = base_datos.obtener_reportes(telefono=telefonos[0])
    if anteriores:
        pantalla.aviso(f"Este número ya tiene {len(anteriores)} reporte(s). Su reporte suma información.")
    while pantalla.confirmar("¿El estafador usó otro número más?"):
        numero = pedir_telefono("Otro número")
        if numero in telefonos:
            pantalla.aviso("Ese número ya está en el reporte.")
        else:
            telefonos.append(numero)

    pantalla.consola.print()
    pais = paises.elegir_pais("¿De qué país es el número? (N°)")
    pantalla.consola.print()
    tipos = elegir_tipos()
    pantalla.consola.print()
    descripcion = pantalla.pedir_texto("¿Qué pasó? Describa la estafa", 2000)

    pantalla.consola.print("\n[dim]Evidencias: capturas, mensajes recibidos, links, etc. "
                           "Escriba una por línea y Enter vacío para terminar.[/]")
    evidencias = []
    while True:
        evidencia = pantalla.pedir_texto(f"Evidencia {len(evidencias) + 1} (opcional)", 500,
                                         obligatorio=False)
        if evidencia == "":
            break
        evidencias.append(evidencia)

    reporte = {
        "telefonos": telefonos,
        "prefijo": pais["prefijo"],
        "tipos": tipos,
        "descripcion": descripcion,
        "evidencias": evidencias,
        "correo_usuario": usuario["correo"],
    }

    nombres_tipos = [t["nombre"] for t in base_datos.obtener_tipos_estafa() if t["ID"] in tipos]
    resumen = Table.grid(padding=(0, 2))
    resumen.add_column(style="bold cyan", justify="right")
    resumen.add_column()
    resumen.add_row("Teléfono(s)", f"[bold]{escape(', '.join(telefonos))}[/]")
    resumen.add_row("País", f"{escape(pais['nombre'])} [dim](+{pais['prefijo']})[/]")
    resumen.add_row("Tipo de estafa", escape(", ".join(nombres_tipos)) or "Sin especificar")
    resumen.add_row("Descripción", escape(descripcion))
    resumen.add_row("Evidencias", str(len(evidencias)))
    pantalla.consola.print()
    pantalla.consola.print(Panel(resumen, title="[bold]Resumen del reporte[/]", title_align="left",
                                 border_style="cyan", box=box.ROUNDED, padding=(1, 2)))

    if not pantalla.confirmar("¿Guardar el reporte?"):
        pantalla.aviso("El reporte no se guardó.")
        pantalla.pausa()
        return

    idr = base_datos.guardar_reporte(reporte)
    pantalla.exito(f"Reporte N° {idr} guardado. Un administrador lo va a revisar.")
    pantalla.pausa()


# ----------------------------------------------------------- Buscar y ver

def buscar_numero(usuario):
    # Opción 2 del menú. Busca los reportes de un número y avisa cuántos
    # fueron confirmados como estafa.
    titulo = "Buscar un número"
    pantalla.encabezado(titulo, usuario)
    pantalla.consola.print("[dim]Antes de responder un mensaje o una llamada, "
                           "fíjese si alguien ya reportó el número.[/]\n")
    numero = pedir_telefono("Número a buscar")

    while True:
        reportes = base_datos.obtener_reportes(telefono=numero)
        pantalla.encabezado(titulo, usuario)

        if not reportes:
            pantalla.consola.print(Panel(
                f"No hay reportes para el número [bold]{escape(numero)}[/].\n"
                "[dim]Igual desconfíe si le piden datos personales, claves o dinero.[/]",
                border_style="green", box=box.ROUNDED, padding=(1, 2)))
            pantalla.pausa()
            return

        confirmados = sum(1 for r in reportes if r["confirmado"])
        texto = f"[bold]¡Atención![/] El número [bold]{escape(numero)}[/] tiene {len(reportes)} reporte(s)"
        if confirmados:
            texto += f", {confirmados} confirmado(s) como estafa"
        pantalla.consola.print(Panel(texto + ".", border_style="red", box=box.HEAVY, padding=(1, 2)))
        mostrar_tabla(reportes)

        if not ver_detalle(reportes, usuario, titulo):
            return


def ver_estafadores(usuario):
    # Opción 3 del menú. Lista todos los reportes guardados y permite ver
    # el detalle de cada uno.
    titulo = "Todos los reportes"
    while True:
        pantalla.encabezado(titulo, usuario)
        reportes = base_datos.obtener_reportes()
        if not reportes:
            pantalla.aviso("Todavía no hay reportes guardados.")
            pantalla.pausa()
            return

        mostrar_tabla(reportes)
        if not ver_detalle(reportes, usuario, titulo):
            return
