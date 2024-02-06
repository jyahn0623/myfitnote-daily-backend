from rest_framework import serializers

from client.models import *

class ClientMeasurementSerializer(serializers.ModelSerializer):
    """사용자 측정 정보"""

    EXERCISE_MAPPING = {
        '측면' : '자세 - 측면',
        '정면' : '자세 - 정면',
    }
    exercise = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = ClientMeasurement
        fields = ('id', 'client', 'count', 'grade', 'created_at', 'exercise')

    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
    
    def get_exercise(self, obj):
        if obj.exercise in self.EXERCISE_MAPPING:
            return self.EXERCISE_MAPPING[obj.exercise]

        return obj.exercise
    

# class FinalClientResultModelSerializer(serializers.Serializer):
#     client = serializers.SerializerMethodField()
#     measurement = serializers.CharField()

#     def get_client(self, obj):
#         return ClientSerializer(obj.client).data