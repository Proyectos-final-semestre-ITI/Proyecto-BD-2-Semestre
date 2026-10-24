# Todo lo que tiene que ver con los estafadores:
# pedir sus datos por consola y mostrarlos.

import base_datos


def agregar_estafador(usuario):
    print()
    print("--- Agregar estafador ---")
    numero = input("Número de teléfono: ")
    pais = input("País: ")
    tipo_estafa = input("Tipo de estafa (opcional): ")
    descripcion = input("Descripción: ")

    estafador = {
        "numero": numero,
        "pais": pais,
        "tipo_estafa": tipo_estafa,
        "descripcion": descripcion,
        # Quién hizo el reporte (en el MER: Usuarios generan Reportes)
        "correo_usuario": usuario["correo"],
    }

    base_datos.guardar_estafador(estafador)


def ver_estafadores():
    print()
    print("--- Lista de estafadores ---")
    lista = base_datos.obtener_estafadores()

    if len(lista) == 0:
        print("No hay estafadores guardados.")
        return

    for estafador in lista:
        print(f"Número: {estafador['numero']} | País: {estafador['pais']} | "
              f"Tipo: {estafador['tipo_estafa']} | Descripción: {estafador['descripcion']} | "
              f"Reportado por: {estafador['correo_usuario']}")
