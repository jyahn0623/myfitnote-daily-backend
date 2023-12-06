from django.urls import path

from client.api.views import *

urlpatterns = [
    path('measurement', ClientMeasurementAPI.as_view()), # 운동 측정
    path('rom', ClientRomAPI.as_view()), # ROM 측정
    path('measurement/final/result',ClientFinalResultAPI.as_view() )
] 
