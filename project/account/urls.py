from django.urls import path
from rest_framework.routers import DefaultRouter

from account.api import views as api_views

# router = DefaultRouter()
# router.register('', api_views.UserAPI, basename='user')

# print(router.urls)

urlpatterns = [
    path('', api_views.UserAPI.as_view({
        'post' : 'create',
        'get' : 'list'
    })),
    path('<int:pk>', api_views.UserAPI.as_view({
        'get' : 'retrieve'
    })),
    path('login', api_views.UserAPI.as_view({
        'post' : 'login'
    })),
    path('question', api_views.UserQuestionAPI.as_view()),
    path('walk', api_views.UserWalkAPI.as_view()),

    path('exercise', api_views.ExerciseAPI.as_view()),
    path('exercise/format/series', api_views.ExerciseSerieseAPI.as_view()),

    # Client
    path('client', api_views.ClientAPI.as_view())
] 
