
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from jusoor_backend.settings import env
from django.conf.urls import static
from django.conf import settings


"""
URL configuration for jusoor_backend project.
"""

schema_view = get_schema_view(
    openapi.Info(
        title="WATCHTOWER API",
        default_version="v2",
        description="WATCHTOWER SERVER",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),
    path('', include(arg='core.urls')),
    path('', include('appointments.urls')),
    # API docs endpoints
    path('chat/', include('chat.urls')),
    re_path(r'', include('sentiment_ai.urls')),
    path('', include('surveys.urls')),
        re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


