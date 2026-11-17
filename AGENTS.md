# AGENTS.md — Gestor SaaS (Control de Stock y Ventas)

Estado del repo tal como está hoy. Todo lo que no se verificó se marca como tal.

## Arquitectura real (verificada en código)

- **Django 4.2 LTS + DRF**, dividido en **4 servicios independientes** que comparten una **misma PostgreSQL** (esquemas separados por servicio). El frontend habla solo con el **gateway**.
- Servicios y puertos: `auth-service` `:8001`, `catalog-service` `:8002`, `sales-service` `:8003`, `gateway` `:8000`.
- Esquemas: `auth_schema`, `catalog_schema`, `sales_schema`. Cada servicio fija su `search_path` en `settings.py`.
- **Gateway** es el punto único de entrada: proxyea `/api/auth/…`, `/api/catalog/…`, `/api/sales/…` a los servicios internos (`gateway/proxy/views.py`) y sirve el frontend vanilla (`gateway/frontend/`). Usa su propia SQLite (`db.sqlite3`).
- **Autenticación:** JWT con `djangorestframework-simplejwt` en auth-service. El login requiere `organization_slug` y devuelve `Bearer` token.
- **Sin CSRF middleware** en ningún servicio (API REST con token en header, no sesiones con cookies).

## Cómo levantar sin Docker (verificado localmente)

Docker no está disponible en este entorno (no se puede iniciar `dockerd` sin sudo). Se levanta contra PostgreSQL local:

1. **PostgreSQL local** (puerto 5433): crear DB `gestor_saas`, usuario `gestor`, esquemas `auth_schema`, `catalog_schema`, `sales_schema`.
2. `cp .env.example .env` y editar:
   - `POSTGRES_HOST=localhost`, `POSTGRES_PORT=5433`
   - `AUTH_SERVICE_URL=http://localhost:8001` (y análogos catalog/sales)
   - `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=True`
3. Crear venv fresco (el `venv/` de la raíz está **roto**, no usarlo):
   ```bash
   python3 -m venv .venv --system-site-packages && source .venv/bin/activate
   pip install -r requirements.txt
   ```
   (`--system-site-packages` reusa `python3-psycopg2` del sistema.)
4. Migraciones por servicio (cada uno con su `manage.py`):
   ```bash
   cd auth-service    && python manage.py migrate
   cd catalog-service && python manage.py migrate
   cd sales-service   && python manage.py migrate
   cd gateway         && python manage.py migrate   # SQLite propia
   ```
5. Levantar los 4 servicios (cada uno en su terminal o con `nohup ... & disown`):
   ```bash
   cd auth-service    && python manage.py runserver 0.0.0.0:8001
   cd catalog-service && python manage.py runserver 0.0.0.0:8002
   cd sales-service   && python manage.py runserver 0.0.0.0:8003
   cd gateway         && python manage.py runserver 0.0.0.0:8000
   ```
6. Acceso: frontend http://localhost:8000, API http://localhost:8000/api/…, health http://localhost:8000/health.

**Nota:** `.env` usa `localhost` para las URLs de servicio (no los DNS de Docker Compose `auth-service:8001`, etc.).

## Endpoints verificados (vía gateway :8000)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/auth/organizations/register` | Crea organización + admin + tokens |
| POST | `/api/auth/login` | Login (necesita `organization_slug`) |
| POST | `/api/auth/logout` | Cierra sesión |
| GET | `/api/auth/me` | Usuario autenticado |
| GET/POST | `/api/catalog/categories` | Categorías (filtro `?organization_id=`) |
| GET/PUT/DELETE | `/api/catalog/categories/<id>` | Detalle categoría |
| GET/POST | `/api/catalog/items` | Ítems (filtro `?organization_id=` y `?search=`) |
| GET/PUT/DELETE | `/api/catalog/items/<id>` | Detalle ítem |
| GET/POST | `/api/catalog/custom-fields` | Campos personalizados |
| GET/POST | `/api/sales/sales` | Ventas (filtro `?organization_id=`) |
| GET | `/api/sales/sales/<id>` | Detalle venta |
| GET | `/api/sales/sales/<id>/items` | Ítems de una venta |
| GET | `/api/sales/inventory-movements` | Movimientos de inventario |

### Caja (`/api/sales/`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/sales/cash-register/open` | Abre caja (una por organización) |
| GET | `/api/sales/cash-register/current?organization_id=` | Caja abierta actual |
| POST | `/api/sales/cash-register/close` | Cierra caja abierta |
| POST | `/api/sales/cash-register/movement` | Movimiento de efectivo (ingreso/egreso) |
| GET | `/api/sales/cash-register/movements?cash_register_id=` | Movimientos de una caja |

### Presupuestos (`/api/sales/`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET/POST | `/api/sales/quotes` | Listar/crear presupuestos (filtro `?organization_id=`, `?status=`) |
| GET/PUT/DELETE | `/api/sales/quotes/<id>` | Detalle/actualizar/eliminar presupuesto |
| POST | `/api/sales/quotes/<id>/accept` | Acepta un presupuesto (solo si está "sent") |

### Clientes (`/api/sales/`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET/POST | `/api/sales/clients` | Listar/crear clientes (filtro `?organization_id=`) |
| GET/PUT/DELETE | `/api/sales/clients/<id>` | Detalle/actualizar/eliminar cliente |

### Facturas AFIP/ARCA (`/api/sales/`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET/POST | `/api/sales/invoices` | Listar/crear facturas (filtro `?organization_id=`, `?status=`) |
| GET/PUT/DELETE | `/api/sales/invoices/<id>` | Detalle/actualizar/eliminar factura |
| POST | `/api/sales/invoices/<id>/request-cae` | Solicita CAE a AFIP (placeholder: sin certificado real no emite CAE válido) |

**Nota ARCA/AFIP:** Para emitir facturas reales se necesita el certificado digital (.p12) y el CUIT de la organización en AFIP. El endpoint `request-cae` es un placeholder que simula el flujo.

## Tests (verificados: 21 pasando, 0 fallos)

Los tests de Django usan **SQLite en memoria** cuando se ejecuta `manage.py test` (no necesitan Postgres):

```bash
cd auth-service    && python manage.py test users     # 9 tests OK
cd catalog-service && python manage.py test catalog   # 6 tests OK
cd sales-service   && python manage.py test sales      # 3 tests OK
```

Total: **18 tests, 0 fallos**. (El README dice "11", está desactualizado.)

## Cambios realizados para que funcione en localhost

- Quitado `CsrfViewMiddleware` de `auth-service`, `catalog-service`, `sales-service`, `gateway` (API REST, token en header).
- Quitado `path('api/', include(...))` de los 3 servicios (ya no necesitan el prefijo; el gateway provee el namespace `/api/auth`, `/api/catalog`, `/api/sales`).
- Simplificado URLs de auth: `/login`, `/logout`, `/me` (sin prefijo `auth/`) para que coincidan con lo que reenvía el gateway.

## Código legacy en la raíz (NO tocar / no extender)

- `app.py`, `database.py`, `templates/`, `pos_system.db`, `seed_database.py`, `check_admin_status.py`, `update_admin_status.py` pertenecen a la **versión original Flask + SQLite**. Son legacy de antes de la migración a Django. Operan sobre `pos_system.db`, no sobre la Postgres de los servicios Django.

## Frontend

- `gateway/frontend/`: `index.html`, `style.css`, `app.js` — vanilla, sin paso de compilación. Se sirve como estático y como SPA.

## Rama y convenciones

- Rama principal: `master`.
- Los scripts en español (voseo), tildes y `ñ`. Los nombres de variables/comentarios también en español.
- Nunca commitear ni pushear sin OK explícito.

## Lo que NO está en este repo

- No hay Supabase, no hay API keys de pago, no hay túneles, no hay Node/Vite.
- No hay tests de integración end-to-end contra Postgres: los tests de Django usan SQLite en memoria.
