

from rest_framework import serializers
from vuelos.models import Avion, Vuelo, Pasajero, Asiento, Reserva, Boleto

class AvionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Avion
		fields = '__all__'

class VueloSerializer(serializers.ModelSerializer):
	avion = AvionSerializer(read_only=True)
	class Meta:
		model = Vuelo
		fields = '__all__'

	def validate_precio_base(self, value):
		if value < 0:
			raise serializers.ValidationError("El precio base no puede ser negativo.")
		return value

class PasajeroSerializer(serializers.ModelSerializer):
	class Meta:
		model = Pasajero
		fields = '__all__'

	def validate_documento(self, value):
		if not value.isdigit():
			raise serializers.ValidationError("El documento debe ser numérico.")
		return value

class AsientoSerializer(serializers.ModelSerializer):
	avion = AvionSerializer(read_only=True)
	class Meta:
		model = Asiento
		fields = '__all__'

class ReservaSerializer(serializers.ModelSerializer):
	vuelo = VueloSerializer(read_only=True)
	pasajero = PasajeroSerializer(read_only=True)
	asiento = AsientoSerializer(read_only=True)
	class Meta:
		model = Reserva
		fields = '__all__'

	def validate_precio(self, value):
		if value < 0:
			raise serializers.ValidationError("El precio no puede ser negativo.")
		return value

class BoletoSerializer(serializers.ModelSerializer):
	reserva = ReservaSerializer(read_only=True)
	class Meta:
		model = Boleto
		fields = '__all__'
