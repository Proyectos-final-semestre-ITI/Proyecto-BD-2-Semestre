# Todo lo que tiene que ver con los usuarios.
# El "inicio de sesión" no es un login real: solo pide los datos del
# usuario para tenerlos guardados mientras el programa está abierto.

import base_datos


def pedir_dato(mensaje):
    # Vuelve a preguntar hasta que se escriba algo
    dato = input(mensaje).strip()
    while dato == "":
        print("Este dato es obligatorio.")
        dato = input(mensaje).strip()
    return dato


def iniciar_sesion():
    print()
    print("--- Iniciar sesión ---")
    correo = pedir_dato("Correo: ").lower()
    while "@" not in correo:
        print("El correo no es válido.")
        correo = pedir_dato("Correo: ").lower()

    # Si el correo ya se usó antes, no se vuelven a pedir los datos
    usuario = base_datos.buscar_usuario(correo)
    if usuario is not None:
        print(f"Bienvenido de nuevo, {usuario['nombre']}.")
        return usuario

    nombre = pedir_dato("Nombre: ")
    pais_origen = pedir_dato("País de origen: ")

    usuario = {
        "correo": correo,
        "nombre": nombre,
        "pais_origen": pais_origen,
    }

    base_datos.guardar_usuario(usuario)
    print(f"Bienvenido, {nombre}.")
    return usuario
