from django.urls import path

from manager import views
from manager.logic_views import center_nrc, center_daekyo

app_name = 'manage'

urlpatterns = [
    path('', views.index, name='index'),
    path('user/inquiry', views.user_inquiry, name='user-inquiry'),
    path('walk/inquiry', views.user_walk_inquiry, name='user-walk-inquiry'),
    path('situp/inquiry', views.user_situp_inquiry, name='user-situp-inquiry'),
    path('eyehand/inquiry', views.user_eyehand_inquiry, name='user-eyehand-inquiry'),
    path('data/<pk>', views.user_data_detail, name='user-walk-detail'),
    # 동작 분석
    path('analysis/pose', views.analysis_pose, name='analysis-pose'),
    # 국립 재활원
    path('npc/data', center_nrc.index),
    path('daekyo/data', center_daekyo.index),
    # 계정 인증
    path('login', views.auth_login, name='login'),
    path('logout', views.auth_logout, name='logout'),
    # 측정 데이터 관리
    path('measurement', views.measurement, name='measurement-management'),
    # 임시: 대교 데이터 저장
    path('measurement/save', views.measurement_save_temp, name='measurement-save-temp'),
    path('measurement/load', views.measurement_load_temp, name='measurement-load-temp'),
    path('measurement/report', views.report)
]