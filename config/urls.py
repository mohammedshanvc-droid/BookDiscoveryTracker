
from django.contrib import admin
from django.urls import path, include
from reading import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_view, name='index'),
    path('accounts/', include('reading.urls')),
    path('reading/', views.reading_view, name='reading'),
    path('api/', include('books.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
