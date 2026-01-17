from pathlib import Path
from datetime import date
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# 1. Definir los usuarios especiales
usuarios = [
    {
        "id_rol": 1,
        "nombre": "Admin",
        "apellidos": "CineFlow",
        "correo": "admin@cineflow.com",
        "telefono": "809-555-0001",
        "fecha_nacimiento": date(1985, 1, 1),
    },
    {
        "id_rol": 2,
        "nombre": "Encargado",
        "apellidos": "Entrada",
        "correo": "encargado_entrada@cineflow.com",
        "telefono": "809-555-0002",
        "fecha_nacimiento": date(1990, 2, 2),
    }
]

# 2. Generar los 50 clientes adicionales
for i in range(1, 51):
    correo_base = f"usuario_{i}"
    usuarios.append({
        "id_rol": 3,
        "nombre": f"Cliente{i}",
        "apellidos": "Apellido",
        "correo": f"{correo_base}@example.com",
        "telefono": f"809-000-{i:04d}",
        "fecha_nacimiento": date(1995, 1, 1),
    })

# --- CAMBIO AQUÍ: Definir archivo en la raíz ---
out_file = Path("crear_usuarios_hash.sql")

lines = []
lines.append("-- Inserts generados para la tabla Usuarios")
lines.append(
    "INSERT INTO Usuarios (IdRol, Nombre, Apellidos, CorreoElectrónico, Teléfono, ContraseñaHash, FechaNacimiento) VALUES"
)

# 3. Procesar y hashear
for i, u in enumerate(usuarios):
    # Contraseña = parte antes del @
    contrasena_plana = u["correo"].split("@")[0]
    pw_hash = bcrypt.generate_password_hash(contrasena_plana).decode("utf-8")
    
    nombre = u["nombre"].replace("'", "''")
    apellidos = u["apellidos"].replace("'", "''")
    correo = u["correo"].replace("'", "''")
    telefono = (u["telefono"] or "").replace("'", "''")
    fecha = f"'{u['fecha_nacimiento'].isoformat()}'" if u.get("fecha_nacimiento") else "NULL"
    
    # Coma para todos menos el último, que lleva punto y coma
    terminador = ";" if i == len(usuarios) - 1 else ","
    
    lines.append(
        f"({u['id_rol']}, '{nombre}', '{apellidos}', '{correo}', '{telefono}', '{pw_hash}', {fecha}){terminador}"
    )

# 4. Escribir el archivo
out_file.write_text("\n".join(lines), encoding="utf-8")
print(f"Éxito: Se ha creado el archivo '{out_file.name}' en la raíz.")