import json
import logging
import collections
import pprint

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.decorators import api_view, action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ModelViewSet

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib import auth
from django.db.models import Q
from django.db import DatabaseError, transaction
from django.http import HttpRequest

from account.models import (
    User,
    ExerciseLog
)
from account.api.serializers import *
from account.utils import *
from manager.logic_views.utils import extrace_value_from_exercise_log

logger = logging.getLogger('django')

class UserQuestionAPI(APIView):
    def post(self, request):
        print(json.loads(request.body))
        print(request.POST)
        return Response({
            "success" : True,
            "message" : "제출이 완료되었어요.\n다음 단계를 진행해 주세요."
            }, status=200)
    

class UserAPI(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request: HttpRequest):
        users = User.objects.all()
        users_srz = self.serializer_class(users, many=True)
        return Response({
            'success' : True,
            'response' : {
                'users' : users_srz.data,
            },
            'error' : None
        }, status=200)

    @action(detail=True, method=['post'])
    def login(self, request):
        print("유저가 로그인을 시도합니다.")
        login_data = json.loads(request.body)
        print(login_data)
        user_auth = authenticate(password=login_data.get('password'), 
                                 username=login_data.get('phone'))
        print(user_auth)
        if user_auth:
            print("로그인 성공")
            token = user_auth.auth_token.key
            return Response({
                "success" : True,
                "user" : {
                    "phone" : user_auth.phone,
                    "name" : user_auth.name,
                    "birth_date" : user_auth.birth_date,
                    "gender" : user_auth.gender,
                    "height" : user_auth.height,
                    "weight" : user_auth.weight,
                    "token" : token
                }
            })
        else:
            return Response({
                "success" : False,
                "user" : None
            })

    
    def retrieve(self, request, pk):
        print('User API retrieve method called', pk)

        user = self.get_queryset().get(pk=pk)
        serializer = self.get_serializer(user)

        return Response(serializer.data, status=200)

    @transaction.atomic()
    def create(self, request):
        print("User API create method called")
        year, month, day = request.data['birth_date'].split('-')
        request.data['birth_date'] = f'{year}-{int(month)+1}-{day}'
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            print("올바른 유저 생성 정보입니다.")
            user = serializer.save()
            token = Token.objects.create(user=user)
            return Response({"success" : True, "message" : "회원가입이 완료되었습니다."}, status=200)
        else:
            logger.error(serializer.errors)
            if 'phone' in serializer.errors:
                message = "이미 사용 중인 핸드폰 번호입니다."
            else:
                message = "모든 정보를 정확히 입력해 주세요."
            return Response({"success" : False, "message" : message}, status=200)

class UserWalkAPI(APIView):
    """
    this class is for user walking exercise.
    """
    def get(self, request):
        walks = Walk.objects.all()
        walks = UserWalkSerializer(walks, many=True).data

        return Response({
            'response' : {
                'data' : walks
            }
        })

    def post(self, request):
        auth_token = request.META.get('HTTP_TOKEN')
        # {"1":[68.66471,166.37798,120.02303,173.74919],"2":[59.293568,147.02933,134.26169,168.0883],"3":[82.79199,148.63336,118.38868,176.12813]}
        print(request.body)
        body_data = request.body
        data = data_to_dict(body_data)

        ExerciseLog.objects.create(
            user=auth_token,
            data=json.loads(body_data),
            type=data.get('type')
        )

        return Response({
            "success" : True,
            }, status=200)

class ExerciseAPI(APIView):
    EXERCISE_KOREAN = {
        'SITUP' : "앉았다 일어서기",
        'WALK' : "걷기",
        'SINGLE_LEGSTANCE' : "외발서기",
        'TUG' : "TUG 운동",
        'SeatDownUp' : "앉았다 일어서기",
        "exercise_balance_line_test" : "균형능력 (일렬자세)",
        "exercise_balance_reverse_line_test" : "균형능력 (반일렬자세)",
        "exercise_balance_test" : "균형능력 (일반자세)",
        "GaitSpeed" : "GaitSpeed"
    }

    def get(self, request):
        exercise_log = ExerciseLog.objects.filter(type__in=['SITUP', 'WALK', 'SINGLE_LEGSTANCE'])[:30]
        # exercise_data = ExerciseLogSerializer(exercise_log, many=True).data
        data = []

        for log in exercise_log:
            json_data = json.loads(log.data)
            exercise = json_data.get('type')
            if exercise == 'SINGLE_LEGSTANCE':
                grade = 1 if json_data.get('grade') else 0
            else:
                grade = json_data.get('grade')

            value = extrace_value_from_exercise_log(log)
            logger.info(value)
            
            _id = log.id    
            data.append({
                'id' : _id,
                'exercise' : ExerciseAPI.EXERCISE_KOREAN.get(exercise),
                'grade' : grade,
                'value' : value, # time or count,
                'created_at' : log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'user' : log.get_user_name()
            })

        return Response(data, status=200)
    
    def post(self, request):
        auth_token = request.META.get('HTTP_TOKEN')
        # {"1":[68.66471,166.37798,120.02303,173.74919],"2":[59.293568,147.02933,134.26169,168.0883],"3":[82.79199,148.63336,118.38868,176.12813]}
        print(request.body)
        body_data = request.body
        data = data_to_dict(body_data)

        ExerciseLog.objects.create(
            user=auth_token,
            data=json.loads(body_data),
            type=data.get('type')
        )

        return Response({
            "success" : True,
            }, status=200)

class ExerciseSerieseAPI(APIView):
    """운동 변화 데이터"""

    def get(self, request):
        """
        일자별 사용자의 데이터 반환
                23.10.11 - 23.10.12 - 23.10.13
        WALK        1         2          3
        SITUP       4         9          2
        SINGLEG     5         6          5

        Data type will be like below
        WALK : [{
            date : 23.10.11,
            value : 10
        }]
        """
        data = ExerciseLog.objects.filter(user="e86a28c1348e6cabc24c336d14ef31ed84a61134",
                                          type__in=['SITUP', 'WALK', 'SINGLE_LEGSTANCE']) \
                                  .order_by('created_at')
        data_dict = collections.defaultdict(list)
        for d in data:
            data_dict[d.type].append({
                'date' : d.created_at.strftime("%Y-%m-%d"),
                'value' : extrace_value_from_exercise_log(d)
            })
        
        pprint.pprint(data_dict)

        return Response(data_dict)