from django.urls import path

from . import views

urlpatterns = [
    path(
        'create-checkout-session/<pk>/',
        views.create_checkout_session,
        name='create_checkout_session',
    ),
    path('cancel/', views.cansel_payment, name='cansel_payment'),
    path('success/', views.success_payment, name='success_payment'),
]
