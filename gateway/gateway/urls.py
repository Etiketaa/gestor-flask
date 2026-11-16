from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve
from proxy import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Archivos estáticos del frontend (CSS, JS)
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATICFILES_DIRS[0]}),

    # Proxy hacia auth-service
    re_path(r'^api/auth/(?P<path>.*)$', views.proxy_auth, name='proxy-auth'),

    # Proxy hacia catalog-service
    re_path(r'^api/catalog/(?P<path>.*)$', views.proxy_catalog, name='proxy-catalog'),

    # Proxy hacia sales-service
    re_path(r'^api/sales/(?P<path>.*)$', views.proxy_sales, name='proxy-sales'),

    # Health check del gateway
    path('health', views.health, name='health'),

    # Frontend: sirve index.html para cualquier otra ruta (SPA simple)
    re_path(r'^(?!api/|admin/|static/|health).*$', views.frontend_view, name='frontend'),
]
