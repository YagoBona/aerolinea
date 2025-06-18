# vuelos/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.lista_vuelos, name='lista_vuelos'),
    path('vuelo/<int:vuelo_id>/', views.detalle_vuelo, name='detalle_vuelo'),
    path('reservar/<int:vuelo_id>/<int:asiento_id>/', views.reservar_asiento, name='reservar_asiento'),
    path('login/', auth_views.LoginView.as_view(template_name='vuelos/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='lista_vuelos'), name='logout'),
    path('registro/', views.registro_usuario, name='registro'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('registro/', views.registro_usuario, name='registro'),
    path('boleto/<str:codigo_reserva>/', views.ver_boleto, name='ver_boleto'),
    path('boleto/imprimir/<str:codigo_reserva>/', views.imprimir_boleto, name='imprimir_boleto'),

]
