"""Mini sistema de ventas por consola (Python + SQLite).

Permite registrar productos, vender y ver el stock y las ventas.
Los datos se guardan en el archivo ventas.db.
"""
import sqlite3

DB = "ventas.db"


def conectar():
    conn = sqlite3.connect(DB)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS productos ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, "
        "precio INTEGER NOT NULL, stock INTEGER NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS ventas ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, producto_id INTEGER NOT NULL, "
        "cantidad INTEGER NOT NULL, total INTEGER NOT NULL, "
        "fecha TEXT DEFAULT CURRENT_TIMESTAMP)"
    )
    return conn


def leer_entero(mensaje):
    while True:
        try:
            valor = int(input(mensaje))
            if valor > 0:
                return valor
        except ValueError:
            pass
        print("Ingresá un número entero mayor a 0.")


def agregar_producto(conn):
    nombre = input("Nombre del producto: ").strip()
    if not nombre:
        print("El nombre no puede estar vacío.")
        return
    precio = leer_entero("Precio (Gs.): ")
    stock = leer_entero("Cantidad en stock: ")
    conn.execute(
        "INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)",
        (nombre, precio, stock),
    )
    conn.commit()
    print("Producto guardado.")


def listar_productos(conn):
    filas = conn.execute("SELECT id, nombre, precio, stock FROM productos").fetchall()
    if not filas:
        print("Todavía no hay productos.")
        return
    print(f"{'ID':<4}{'Producto':<20}{'Precio':>10}{'Stock':>8}")
    for id_, nombre, precio, stock in filas:
        print(f"{id_:<4}{nombre:<20}{precio:>10}{stock:>8}")


def vender(conn):
    listar_productos(conn)
    id_producto = leer_entero("ID del producto a vender: ")
    fila = conn.execute(
        "SELECT precio, stock FROM productos WHERE id = ?", (id_producto,)
    ).fetchone()
    if fila is None:
        print("Ese producto no existe.")
        return
    precio, stock = fila
    cantidad = leer_entero("Cantidad: ")
    if cantidad > stock:
        print(f"No alcanza el stock (disponible: {stock}).")
        return
    total = precio * cantidad
    conn.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cantidad, id_producto))
    conn.execute(
        "INSERT INTO ventas (producto_id, cantidad, total) VALUES (?, ?, ?)",
        (id_producto, cantidad, total),
    )
    conn.commit()
    print(f"Venta registrada. Total: {total} Gs.")


def ver_ventas(conn):
    filas = conn.execute(
        "SELECT v.fecha, p.nombre, v.cantidad, v.total "
        "FROM ventas v JOIN productos p ON p.id = v.producto_id ORDER BY v.id"
    ).fetchall()
    if not filas:
        print("Todavía no hay ventas.")
        return
    for fecha, nombre, cantidad, total in filas:
        print(f"{fecha} | {nombre} x{cantidad} = {total} Gs.")
    print(f"Total vendido: {sum(f[3] for f in filas)} Gs.")


def main():
    conn = conectar()
    opciones = {
        "1": ("Agregar producto", agregar_producto),
        "2": ("Ver productos y stock", listar_productos),
        "3": ("Registrar venta", vender),
        "4": ("Ver ventas", ver_ventas),
    }
    while True:
        print("\n--- MINI SISTEMA DE VENTAS ---")
        for clave, (texto, _) in opciones.items():
            print(f"{clave}. {texto}")
        print("0. Salir")
        eleccion = input("Elegí una opción: ").strip()
        if eleccion == "0":
            break
        if eleccion in opciones:
            opciones[eleccion][1](conn)
        else:
            print("Opción inválida.")
    conn.close()


if __name__ == "__main__":
    main()
