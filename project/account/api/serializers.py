from rest_framework import serializers
from account.models import *

class UserSerializer(serializers.ModelSerializer):
    auth_token = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (('phone', 'password', 'name', 'birth_date', 'gender', 'height', 'weight'))
    
    def auth_token(self, obj):
        return self.get_token(obj)
        
    def get_token(self, obj):
        if obj.auth_token:
            return obj.auth_token.key
        return None

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        try:
            user.set_password(validated_data['password'])
            user.save()
        except KeyError:
            pass
        return user


class ExerciseLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseLog
        fields = '__all__'