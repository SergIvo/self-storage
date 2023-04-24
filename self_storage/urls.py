from django.contrib import admin
from django.urls import path, include

from storage import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('boxes/', views.get_boxes, name='boxes'),
    path('faq/', views.get_faq, name='faq'),
    path('confidential/', views.get_confidential, name='confidential'),
    path('account/', views.get_account, name='account'),
    path('logout/', views.logout_user, name="logout"),
    path('login/', views.login_user, name="login"),
    path('register/', views.register_user, name="register_user"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
