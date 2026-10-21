# Menú principal del programa. Ejecutar con:  python menu.py

import estafadores


def mostrar_menu():
    print()
    print("===== PROGRAMA ANTI-ESTAFAS =====")
    print("1. Agregar estafador")
    print("2. Ver lista de estafadores")
    print("0. Salir")


def main():
    while True:
        mostrar_menu()
        opcion = input("Elija una opción: ")

        if opcion == "1":
            estafadores.agregar_estafador()
        elif opcion == "2":
            estafadores.ver_estafadores()
        elif opcion == "0":
            print("Saliendo del programa...")
            break
        else:
            print("Opción inválida, intente de nuevo.")


if __name__ == "__main__":
    main()
