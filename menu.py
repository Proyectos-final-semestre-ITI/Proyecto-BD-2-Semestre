# Menú principal del programa. Ejecutar con:  python menu.py

import estafadores
import usuarios


def mostrar_menu(usuario):
    print()
    print("===== PROGRAMA ANTI-ESTAFAS =====")
    print(f"Usuario: {usuario['nombre']} ({usuario['correo']})")
    print("1. Agregar estafador")
    print("2. Ver lista de estafadores")
    print("3. Cerrar sesión")
    print("0. Salir")


def main():
    usuario = usuarios.iniciar_sesion()

    while True:
        mostrar_menu(usuario)
        opcion = input("Elija una opción: ")

        if opcion == "1":
            estafadores.agregar_estafador(usuario)
        elif opcion == "2":
            estafadores.ver_estafadores()
        elif opcion == "3":
            print(f"Hasta luego, {usuario['nombre']}.")
            usuario = usuarios.iniciar_sesion()
        elif opcion == "0":
            print("Saliendo del programa...")
            break
        else:
            print("Opción inválida, intente de nuevo.")


if __name__ == "__main__":
    main()
