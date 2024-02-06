
from django.urls import path

from prescription.api.views import PrescriptionViewSet

urlpatterns = [
    path('', PrescriptionViewSet.as_view({'get': 'list', 'post': 'create'}), name='prescription-list'),
    path('<int:pk>/', PrescriptionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='prescription-detail'),
    path('today/', PrescriptionViewSet.as_view({'get': 'get_today_prescription'}), name='prescription-today'),
    path('make/', PrescriptionViewSet.as_view({'post': 'make_prescription'}), name='prescription-make'),
]
