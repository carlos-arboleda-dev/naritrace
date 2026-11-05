from rest_framework import serializers
from .models import Usuario

class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'rol', 'telefono', 'municipio']
        
    def create(self, validated_data):
        # Extraemos la contraseña para encriptarla
        password = validated_data.pop('password')
        
        # Creamos el usuario
        usuario = Usuario(**validated_data)
        usuario.set_password(password) # Encripta la contraseña
        usuario.save()
        return usuario