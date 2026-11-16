# Gestor SaaS — Control de Stock y Ventas

Sistema de control de stock y ventas orientado a **cualquier rubro**, diseñado como un **SaaS multiempresa** que cualquier cliente pueda instalar, configurar y adaptar a su manera.

## Arquitectura

Backend dividido en **4 servicios Django independientes** que comparten una misma base de datos PostgreSQL (esquemas separados por servicio). El frontend habla solo con un **gateway** que actúa como punto único de entrada.

| Servicio | Responsabilidad | Puerto |
|----------|-----------------|--------|
| `auth-service` | Organizaciones, usuarios, roles, login/registro | `:8001` |
| `catalog-service` | Categorías, ítems, campos personalizados | `:8002` |
| `sales-service` | Ventas, ítems de venta, movimientos de inventario | `:8003` |
| `gateway` | Proxy único + frontend servido (misma origen) | `:8000` |
| `db` | PostgreSQL 15 | `:5432` |

## Tecnologías

- **Backend:** Django 4.2 LTS + Django REST Framework
- **Base de datos:** PostgreSQL 15 (sin Supabase)
- **Despliegue:** Docker + Docker Compose
- **Frontend:** HTML/CSS/JS vanilla (sin dependencias de compilación)
- **Tests:** `unittest` de Django (11 tests pasando)
- **Licencia:** MIT

## Estructura del proyecto

```
gestor-django-saas/
├── .env.example          # Variables de entorno
├── .gitignore
├── LICENSE               # Licencia MIT
├── README.md
├── docker-compose.yml    # Orquestación completa
├── postgres/
│   └── init.sql          # Esquemas aislados por servicio
├── auth-service/         # Django app
│   └── users/            # Organization, Role, User
├── catalog-service/      # Django app
│   └── catalog/          # Category, Item, CustomFieldDefinition
├── sales-service/        # Django app
│   └── sales/            # Sale, SaleItem, InventoryMovement
└── gateway/              # Django app + frontend
    ├── proxy/            # Reenvío a servicios internos
    └── frontend/         # index.html, style.css, app.js
```

## Cómo empezar

### 1. Clona el repositorio

```bash
git clone https://github.com/Etiketaa/gestor-flask.git
cd gestor-flask
```

### 2. Configura variables de entorno

```bash
cp .env.example .env
# Edita .env con tus valores (SECRET_KEY, contraseñas de Postgres, etc.)
```

### 3. Levanta todo con Docker

```bash
docker-compose up -d
```

Esto levanta PostgreSQL, auth-service, catalog-service, sales-service y el gateway.

### 4. Accede a la aplicación

- Frontend: http://localhost:8000
- API Gateway: http://localhost:8000/api/...
- Health check: http://localhost:8000/health

## Endpoints principales

### Autenticación (`/api/auth/`)
- `POST /organizations/register` — Crea organización + primer admin
- `POST /auth/login` — Inicia sesión (necesita `organization_slug`)
- `POST /auth/logout` — Cierra sesión
- `GET /auth/me` — Usuario autenticado

### Catálogo (`/api/catalog/`)
- `GET/POST /categories` — Categorías
- `GET/PUT/DELETE /categories/<id>` — Detalle de categoría
- `GET/POST /items` — Ítems (con `custom_fields` JSON)
- `GET/PUT/DELETE /items/<id>` — Detalle de ítem
- `GET/POST /custom-fields` — Campos personalizados por organización
- `GET/PUT/DELETE /custom-fields/<id>` — Detalle de campo personalizado

### Ventas (`/api/sales/`)
- `GET/POST /sales` — Ventas
- `GET /sales/<id>` — Detalle de venta
- `GET /sales/<id>/items` — Ítems de una venta
- `GET /inventory-movements` — Movimientos de inventario

## Variables de entorno (.env)

```bash
DJANGO_SECRET_KEY=cambia-esta-clave-por-algo-seguro
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=gestor_saas
POSTGRES_USER=gestor
POSTGRES_PASSWORD=gestor123
POSTGRES_HOST=db
POSTGRES_PORT=5432

AUTH_SERVICE_URL=http://auth-service:8001
CATALOG_SERVICE_URL=http://catalog-service:8002
SALES_SERVICE_URL=http://sales-service:8003
```

## Tests

```bash
cd auth-service && python manage.py test users
cd catalog-service && python manage.py test catalog
cd sales-service && python manage.py test sales
```

Resultado: **11 tests pasando, 0 fallos.**

## Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).

---

¿Querés colaborar? Abrí un issue o enviá un pull request a la rama `master`.
