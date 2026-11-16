-- Esquemas separados por servicio dentro de la misma base de datos
CREATE SCHEMA IF NOT EXISTS auth_schema;
CREATE SCHEMA IF NOT EXISTS catalog_schema;
CREATE SCHEMA IF NOT EXISTS sales_schema;

-- Búsqueda de esquema por defecto (ajustable por servicio vía Django)
ALTER DATABASE gestor_saas SET search_path TO auth_schema, catalog_schema, sales_schema, public;
