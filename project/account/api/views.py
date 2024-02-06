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
from django.db.utils import IntegrityError
from django.http import HttpRequest
from django.core.exceptions import ValidationError

from account.models import (
    User,
    ExerciseLog
)
from account.api.serializers import *
from account.utils import *
from manager.logic_views.utils import extrace_value_from_exercise_log

logger = logging.getLogger('application')

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

    @action(detail=False, method=['post'])
    def login(self, request):
        logger.info(f"로그인 요청 - {request.body}")
        login_data = json.loads(request.body)
        user_auth = authenticate(password=login_data.get('password'), 
                                 username=login_data.get('username'))
        if user_auth:
            token = user_auth.auth_token.key
            user_type = user_auth.user_type
            logger.info(f"로그인 성공 {user_auth} | TYPE: {user_type}")
            user_data = {
                "success" : True,
                "user" : {
                    "userType" : user_type,
                    "username" : user_auth.username,
                    # "name" : user_auth.name,
                    # "birth_date" : user_auth.birth_date,
                    # "gender" : user_auth.gender,
                    # "height" : user_auth.height,
                    # "weight" : user_auth.weight,
                    "token" : token,
                }
            }

            if user_type == 2:
                # 기관 관리자인 경우 해당 기업의 정보도 함께 반환
                user_data.update({
                    "manager" : CompanyManagerSerializer(user_auth.companymanager).data
                }) 
            elif user_type == 1:
                # 일반 사용자인 경우 해당 사용자의 정보도 함께 반환
                user_data.update({
                    "client" : ClientSerializer(user_auth.client).data
                })

            return Response(user_data)
        else:
            logger.info(f"로그인 실패")
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
    
class ClientAPI(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        """기업 관리자가 고객을 생성할 경우 호출"""
        data = json.loads(request.body)
        client = None
        success = False
        message = "고객 등록에 실패하였습니다."

        fields = ['birth_date', 'name', 'phone', 'gender', 'height', 'weight', 'address']
        query = {}

        for field in fields:
            value = data.get(field)
            
            if field == 'birth_date':
                value = f'{value[:4]}-{value[4:6]}-{value[6:]}'

            query[field] = value
        
        manager_id_number = data['manager']['id_number']
        manager_company_name = data['manager']['company']['name']

        manager = CompanyManager.objects.get(id_number=manager_id_number,
                                             company__name=manager_company_name)
        query.update({
            "manager" : manager
        })

        logger.info(f"{manager.company.name} | {manager.name} ({manager.id_number})가 새로운 고객 등록 시도 - {data}")

        # 유저 생성
        try:
            with transaction.atomic():
                user = User.objects.create_user(username=manager.company.code + data['phone'],
                                                password=data['phone'],
                                                user_type=1)
                print(user)
                token = Token.objects.create(user=user)
                client = Client(user=user, **query)
                client.save()
                # client.user = user
                # client.save(update_fields=['user'])

                logger.info(f"{manager.company.name} | {manager.name} ({manager.id_number})가 성공적으로 고객 등록 - {data}")
                success = True
                message = f"성공적으로 고객을 생성하였습니다.\n아이디 : {user.username}입니다.\n비밀번호 : {data['phone']}입니다."
        except ValidationError as err:
            message = "이미 등록된 고객입니다."
            logger.error(f"{manager.company.name} | {manager.name} ({manager.id_number})가 고객 등록 도중 오류 발생", exc_info=True)
        
        except IntegrityError as err:
            logger.error(f"{manager.company.name} | {manager.name} ({manager.id_number})가 고객 등록 도중 오류 발생 | IntegrityError", exc_info=True)

        context = {
            'success' : success,
            'message' : message,
            'client' : ClientSerializer(client).data
        }

        return Response(context, 200)
    
    def get(self, request):
        
        name = request.GET.get('name')

        # 기업 관리자의 고객 목록 반환
        if name:
            clients = Client.objects.filter(manager__user=request.user,
                                            name__contains=name)
        else:
            clients = Client.objects.filter(manager__user=request.user)
        clients_data = ClientSerializer(clients, many=True).data

        return Response(clients_data, status=200)