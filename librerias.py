# Verificación de las librerías externas que necesita el programa.
# Se ejecuta antes que el resto, ya que los demás archivos importan
# rich y mysql.connector al abrirse.

import importlib
import importlib.util
import subprocess
import sys

# Nombre del módulo -> nombre del paquete en pip
LIBRERIAS = {
    "mysql.connector": "mysql-connector-python",
    "rich": "rich",
}


def esta_instalado(modulo):
    # Comprueba si el módulo está disponible, sin llegar a importarlo
    try:
        return importlib.util.find_spec(modulo) is not None
    except ModuleNotFoundError:
        # Ocurre con "mysql.connector" cuando no existe el paquete "mysql"
        return False


def faltantes():
    # Paquetes de pip que todavía no están instalados
    importlib.invalidate_caches()
    return [paquete for modulo, paquete in LIBRERIAS.items() if not esta_instalado(modulo)]


def verificar():
    # Si falta alguna librería, la informa y ofrece instalarla con pip.
    # Si no queda instalada, el programa se cierra.
    paquetes = faltantes()
    if not paquetes:
        return

    print("Faltan librerías necesarias para ejecutar el programa:")
    for paquete in paquetes:
        print(f"  - {paquete}")
    print()

    # En el ejecutable las librerías ya vienen incluidas; no se puede usar pip
    if not getattr(sys, "frozen", False):
        respuesta = input("¿Desea instalarlas ahora? (s/n): ").strip().lower()
        if respuesta in ("s", "si", "sí"):
            subprocess.run([sys.executable, "-m", "pip", "install", *paquetes])
            if not faltantes():
                print("\nLibrerías instaladas correctamente.\n")
                return
            print("\nNo se pudieron instalar las librerías.")

        print("Para instalarlas manualmente:")
        print(f"  pip install {' '.join(paquetes)}")

    input("\nPresione Enter para salir...")
    sys.exit(1)
