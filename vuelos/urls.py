# vuelos/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import LoginView
from vuelos.forms import FormularioLogin

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('inicio/', views.inicio, name='inicio'),
    path('vuelos/', views.lista_vuelos, name='lista_vuelos'),
    path('vuelo/<int:vuelo_id>/', views.detalle_vuelo, name='detalle_vuelo'),
    path('reservar/<int:vuelo_id>/<int:asiento_id>/', views.reservar_asiento, name='reservar_asiento'),
    path('login/', LoginView.as_view(
            template_name='vuelos/login.html',
            authentication_form=FormularioLogin
        ), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('registro/', views.registro_usuario, name='registro'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('registro/', views.registro_usuario, name='registro'),
    path('boleto/<str:codigo_reserva>/', views.ver_boleto, name='ver_boleto'),
    path('boleto/imprimir/<str:codigo_reserva>/', views.imprimir_boleto, name='imprimir_boleto'),
    path('cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
]
