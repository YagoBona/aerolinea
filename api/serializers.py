

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
		read_only_fields = ('estado', 'fecha_reserva', 'codigo_reserva')

	def validate_precio(self, value):
		if value < 0:
			raise serializers.ValidationError("El precio no puede ser negativo.")
		return value


class ReservaCreateSerializer(serializers.ModelSerializer):
	"""Serializer para creación de reservas usando IDs (pasajero, vuelo, asiento)."""
	pasajero = serializers.PrimaryKeyRelatedField(queryset=Pasajero.objects.all())
	vuelo = serializers.PrimaryKeyRelatedField(queryset=Vuelo.objects.all())
	asiento = serializers.PrimaryKeyRelatedField(queryset=Asiento.objects.all())

	class Meta:
		model = Reserva
		fields = ('id', 'pasajero', 'vuelo', 'asiento', 'precio')

	def validate(self, attrs):
		vuelo = attrs.get('vuelo')
		asiento = attrs.get('asiento')
		if asiento.avion_id != vuelo.avion_id:
			raise serializers.ValidationError('El asiento no pertenece al avión del vuelo')
		conflict = Reserva.objects.filter(
			vuelo=vuelo, asiento=asiento, estado__in=['confirmada', 'pendiente']
		).exists()
		if conflict:
			raise serializers.ValidationError('Asiento no disponible para ese vuelo')
		return attrs

class BoletoSerializer(serializers.ModelSerializer):
	reserva = ReservaSerializer(read_only=True)
	class Meta:
		model = Boleto
		fields = '__all__'
