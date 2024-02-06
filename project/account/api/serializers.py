import datetime

from rest_framework import serializers

from account.models import *
from client.api.serializers import ClientMeasurementSerializer

class UserSerializer(serializers.ModelSerializer):
    auth_token = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(write_only=True)
    user_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (('username', 'password', 'user_type'))
    
    def auth_token(self, obj):
        return self.get_token(obj)
        
    def get_token(self, obj):
        if obj.auth_token:
            return obj.auth_token.key
        return None
    
    def get_user_type(self, obj):
        if obj.user_type == 1:
            return "고객"
        elif obj.user_type == 2:
            return "담당자"

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


class CompanyManagerSerializer(serializers.ModelSerializer):
    total_client_cnt = serializers.SerializerMethodField()
    new_clint_cnt = serializers.SerializerMethodField()
    class Meta:
        model = CompanyManager
        fields = ('user', 'company', 'id_number', 'phone', 'name', 'total_client_cnt', 'new_clint_cnt')
        depth = 1

    def get_total_client_cnt(self, obj): 
        return obj.client_set.count()

    def get_new_clint_cnt(self, obj): 
        today = datetime.datetime.today()
        return obj.client_set.filter(created_at__year=today.year,
                                    created_at__month=today.month,
                                    created_at__day=today.day).count()
    
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('name', 'logo', 'primary_color')
        depth = 1

class ClientSerializer(serializers.ModelSerializer):
    """Client Serializer for android account.model.Client"""
    last_measurement = serializers.SerializerMethodField() # 최근 검사 항목
    username = serializers.SerializerMethodField() # 사용자 아이디
    token = serializers.SerializerMethodField() # 사용자 토큰
    class Meta:
        model = Client
        fields = ('name', 'phone', 'birth_date', 'gender', 'height', 'weight', 'address', 'manager', 'last_measurement', 'username', 'token')
        depth = 2

    def get_last_measurement(self, client):
        """사용자의 최근 측정 정보"""
        last_measurement = client.clientmeasurement_set.first()
        data = ClientMeasurementSerializer(last_measurement).data
        return data

    def get_username(self, client):
        """사용자 아이디"""
        if client.user:
            return client.user.username
        return None
    
    def get_token(self, client):
        if client.user:
            return client.user.auth_token.key
        return None