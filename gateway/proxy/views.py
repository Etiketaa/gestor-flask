import requests
from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings
from pathlib import Path


def _add_cors(response):
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken, Cookie'
    response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
    response['Access-Control-Allow-Credentials'] = 'true'
    return response


def _forward(request, service_url, path):
    """
    Reenvía una petición HTTP al servicio destino y devuelve su respuesta.
    """
    # Manejo de preflight CORS
    if request.method == 'OPTIONS':
        return _add_cors(HttpResponse(status=200))

    url = f"{service_url.rstrip('/')}/{path.lstrip('/')}"

    method = request.method.lower()
    data = request.body if method in ('post', 'put', 'patch', 'delete') else None
    params = request.GET.dict()

    headers = {}
    if request.content_type:
        headers['Content-Type'] = request.content_type

    cookies = request.COOKIES

    try:
        resp = requests.request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            timeout=15,
            allow_redirects=False,
        )
    except requests.RequestException as e:
        return _add_cors(HttpResponse(
            f'Error conectando con servicio: {e}',
            status=502,
            content_type='text/plain',
        ))

    response = HttpResponse(
        content=resp.content,
        status=resp.status_code,
    )

    for header in ('Content-Type', 'Cache-Control'):
        if header in resp.headers:
            response[header] = resp.headers[header]

    # Reenviar Set-Cookie (sesiones de auth-service, etc.)
    if 'Set-Cookie' in resp.headers:
        value = resp.headers['Set-Cookie']
        if isinstance(value, list):
            for cookie in value:
                response['Set-Cookie'] = cookie
        else:
            response['Set-Cookie'] = value

    return _add_cors(response)


def proxy_auth(request, path):
    return _forward(request, settings.AUTH_SERVICE_URL, path)


def proxy_catalog(request, path):
    return _forward(request, settings.CATALOG_SERVICE_URL, path)


def proxy_sales(request, path):
    return _forward(request, settings.SALES_SERVICE_URL, path)


def health(request):
    return HttpResponse('ok', status=200, content_type='text/plain')


def frontend_view(request, path=''):
    """Sirve index.html del frontend para cualquier ruta no API (SPA simple)."""
    index_path = Path(settings.STATICFILES_DIRS[0]) / 'index.html'
    if index_path.exists():
        return HttpResponse(index_path.read_text(encoding='utf-8'), content_type='text/html')
    return HttpResponse('Frontend no encontrado', status=404, content_type='text/plain')
