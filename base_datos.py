#futura concecion a base de datos

# Mientras no haya base de datos, los datos se guardan en estas listas.
# Se pierden al cerrar el programa.
usuarios = []
estafadores = []


def guardar_usuario(usuario):
    # TODO: hacer el INSERT en la base de datos
    usuarios.append(usuario)


def buscar_usuario(correo):
    # TODO: hacer el SELECT ... WHERE correo = ... en la base de datos
    for usuario in usuarios:
        if usuario["correo"] == correo:
            return usuario
    return None


def guardar_estafador(estafador):
    # TODO: hacer el INSERT en la base de datos
    estafadores.append(estafador)
    print("Estafador guardado.")


def obtener_estafadores():
    # TODO: hacer el SELECT en la base de datos
    return estafadores
