from django.contrib import admin
from django.urls import path, re_path
from core.views import home, page, wallet_submit
from django.conf import settings
from django.conf.urls.static import static
from core import views  
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("core.urls")),
    path('api/wallet/submit/', views.wallet_submit, name='wallet_submit'),
    path('',views.home, name='home'),
    re_path(r'^(?P<name>[^/]+?)(\.html)?/?$', views.page, name='page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
