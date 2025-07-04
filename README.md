# Sistema de Punto de Venta (POS) con Flask

Este es un sistema de Punto de Venta (POS) basado en la web, desarrollado con Flask. Permite la gestión de usuarios, productos, categorías, ventas e inventario.

## Características

- **Gestión de usuarios:**
    - Registro de nuevos usuarios con aprobación pendiente.
    - Inicio y cierre de sesión.
    - Roles de usuario (administrador, depósito, venta).
    - Panel de administrador para aprobar o rechazar nuevos usuarios.
- **Gestión de productos:**
    - Crear, leer, actualizar y eliminar (CRUD) productos.
    - Asignación de categorías a los productos.
    - Carga de imágenes de productos.
    - Generación automática de SKU.
- **Gestión de categorías:**
    - CRUD de categorías de productos.
- **Ventas:**
    - Procesamiento de ventas.
    - Historial de ventas.
- **Gestión de inventario:**
    - Seguimiento de los movimientos de inventario (stock inicial, ajustes, ventas).

## Tecnologías utilizadas

- **Backend:** Flask (Python)
- **Base de datos:** SQLite
- **Frontend:** HTML, CSS, JavaScript (con plantillas Jinja2)

## Estructura del proyecto

```
/media/franco/Reservado para el sistema/pos_flask_app/
├───app.py                  # Archivo principal de la aplicación Flask
├───database.py             # Funciones para inicializar y conectar a la base de datos
├───pos_system.db           # Archivo de la base de datos SQLite
├───seed_database.py        # Script para poblar la base de datos con datos iniciales
├───templates/              # Plantillas HTML
│   ├───admin_users.html
│   ├───dashboard.html
│   ├───index.html
│   ├───login.html
│   └───register.html
└───venv/                   # Entorno virtual de Python
```

## Cómo empezar

1. **Clona el repositorio:**
   ```bash
   git clone <url-del-repositorio>
   cd pos_flask_app
   ```

2. **Crea e inicializa un entorno virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instala las dependencias:**
   ```bash
   pip install Flask
   ```

4. **Inicializa y puebla la base de datos:**
   ```bash
   python seed_database.py
   ```

5. **Ejecuta la aplicación:**
   ```bash
   python app.py
   ```

6. **Accede a la aplicación:**
   Abre tu navegador y ve a `http://127.0.0.1:5000`.

## Usuarios de prueba

| Usuario  | Contraseña | Rol         |
|----------|------------|-------------|
| admin1   | admin1     | admin       |
| admin2   | admin2     | admin       |
| admin3   | admin3     | admin       |
| depo1    | depo1      | depo        |
| venta1   | venta1     | venta       |
