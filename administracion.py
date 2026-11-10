# Opciones que solo ven los administradores

import base_datos
import estafadores
import pantalla


def revisar_reportes(usuario):
    # Opción 4 del menú (solo administradores). Lista los reportes pendientes
    # y permite elegir uno para revisarlo.
    titulo = "Revisar reportes pendientes"
    while True:
        pantalla.encabezado(titulo, usuario)
        pendientes = base_datos.obtener_reportes(solo_pendientes=True)
        if not pendientes:
            pantalla.exito("No hay reportes pendientes de revisión.")
            pantalla.pausa()
            return

        estafadores.mostrar_tabla(pendientes)
        idr = pantalla.pedir_numero("\nN° de reporte a revisar (Enter para volver)", 1, obligatorio=False)
        if idr is None:
            return

        reporte = next((r for r in pendientes if r["IDR"] == idr), None)
        if reporte is None:
            pantalla.error("Ese reporte no está en la lista de pendientes.")
            pantalla.pausa()
            continue

        revisar(reporte, usuario)


def revisar(reporte, usuario):
    # Muestra el reporte, pide la prioridad y la decisión del administrador
    # y guarda la revisión en la tabla Aceptan
    pantalla.encabezado(f"Revisar reporte N° {reporte['IDR']}", usuario)
    estafadores.mostrar_detalle(reporte)

    pantalla.consola.print("\n[bold]Prioridad del reporte[/]")
    prioridad = pantalla.menu([
        ("1", "[green]Baja[/]"),
        ("2", "[yellow]Media[/]"),
        ("3", "[red]Alta[/]"),
    ], "Prioridad")

    pantalla.consola.print("\n[bold]¿Qué decide?[/]")
    opcion = pantalla.menu([
        ("1", "[bold red]Confirmar[/] que es una estafa"),
        ("2", "[dim]Descartar[/] el reporte"),
        ("3", "[yellow]Dejarlo pendiente[/] (solo guardar la prioridad)"),
    ], "Decisión")
    estado = {"1": "confirmado", "2": "cancelado", "3": "pendiente"}[opcion]

    base_datos.guardar_revision(reporte["IDR"], usuario["correo"], int(prioridad), estado)
    pantalla.consola.print()
    pantalla.exito(f"Reporte N° {reporte['IDR']} revisado.")
    pantalla.pausa()
