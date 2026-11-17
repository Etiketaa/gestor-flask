#!/bin/bash
set -a
. /home/franco/gestor-django-saas/.env
set +a
cd /home/franco/gestor-django-saas
source .venv/bin/activate

nohup python auth-service/manage.py runserver 0.0.0.0:8001 > /tmp/auth.log 2>&1 &
nohup python catalog-service/manage.py runserver 0.0.0.0:8002 > /tmp/catalog.log 2>&1 &
nohup python sales-service/manage.py runserver 0.0.0.0:8003 > /tmp/sales.log 2>&1 &
nohup python gateway/manage.py runserver 0.0.0.0:8000 > /tmp/gateway.log 2>&1 &

echo "Servicios iniciados. Esperando a que estén listos..."
sleep 8
curl -s http://localhost:8000/health && echo ""
echo "Hecho."
