from rest_framework import serializers

from prescription.models import Prescription, PrescriptionDetail

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'
        depth = 1



class PrescriptionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionDetail
        exclude = ('prescription', )
        depth = 1 