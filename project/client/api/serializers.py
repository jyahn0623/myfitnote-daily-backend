from rest_framework import serializers

from client.models import *

class ClientMeasurementSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = ClientMeasurement
        fields = ('id', 'client', 'count', 'grade', 'created_at', 'exercise')

    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")

# class FinalClientResultModelSerializer(serializers.Serializer):
#     client = serializers.SerializerMethodField()
#     measurement = serializers.CharField()

#     def get_client(self, obj):
#         return ClientSerializer(obj.client).data