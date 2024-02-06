import pprint
import json
import logging
import base64
import os

from django.core.files.base import ContentFile

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication

from account.models import Client
from account.api.serializers import ClientSerializer
from client.models import ClientMeasurement
from client.api.serializers import *

logger = logging.getLogger('application')

class ClientMeasurementAPI(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        """
        This map to ClientMeasurementResultData of Android. 
        """
        print(request.GET)

        client_name = request.GET.get("name")
        client_phone = request.GET.get("phone")

        client = Client.objects.filter(manager=request.user.companymanager,
                                       name=client_name,
                                       phone=client_phone).first()

        data = ClientMeasurement.objects.filter(client=client)
        data_srz = ClientMeasurementSerializer(data, many=True).data

        return Response(data_srz, status=200)
        

    def post(self, request):
        data = json.loads(request.body)
        print(data)
        
        manager = request.user.companymanager
        client_name = data.get("name")
        client_phone = data.get("phone")

        try:
            client = Client.objects.filter(manager=manager,
                                           name=client_name,
                                           phone=client_phone).first()
            logger.info(f'{manager}이 클라이언트 ({client})를 측정하였습니다.')
            test_result = data.get("testResult")
            exercise = data.get("exercise")
            
            if data.get("exercise") == "외발서기":
                side = data.get('testResult').get('side')
                if side == "왼발":
                    exercise = "외발서기 (좌)"
                else:
                    exercise = "외발서기 (우)"

            measurement = ClientMeasurement.objects.create(
                client=client,
                count=test_result.get("count"),
                grade=test_result.get("grade"),
                exercise=exercise,
                raw_data=data.get("testResult"))
            logger.info(f'{manager}이 클라이언트 ({client}) 측정 기록 저장을 완료하였습니다. - {measurement.pk}')

        except Exception as err:
            logger.error(f'{manager}이 측정 결과 처리 도중 문제가 발생하였습니다.', exc_info=True)

        return Response({}, status=200)

    def delete(self, request):
        print(request.GET)
        
        checkedResultIds = request.GET.getlist("checkedResultIds")

        try:
            measurement = ClientMeasurement.objects.filter(id__in=checkedResultIds)
            measurement.delete()
            logger.info(f'측정 기록 ({measurement}) 삭제를 완료하였습니다.')
            return Response({
                'message' : "측정 기록 삭제를 완료하였습니다.",
                'success' : True,
            })
        except Exception as err:
            logger.error(f'측정 기록 삭제 도중 문제가 발생하였습니다.', exc_info=True)
            return Response({
                'message' : "측정 기록 삭제 도중 문제가 발생하였습니다.",
                'success' : False,
            })
class ClientRomAPI(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        print(request.POST, request.FILES)
        data = json.loads(request.POST.get("result"))
        result_image = request.FILES.get("image")
        
        manager = request.user.companymanager
        client_name = data.get("name")
        client_phone = data.get("phone")
        try:
            client = Client.objects.filter(manager=manager,
                                           name=client_name,
                                           phone=client_phone).first()
            logger.info(f'ClientRomAPI - {manager}이 클라이언트 ({client})를 측정하였습니다.')

            measurement = ClientMeasurement.objects.create(
                client=client,
                count=data.get("angle"),
                exercise=data.get("type"))

            if result_image:
                logger.info(f"ClientRomAPI - {client}의 측정 이미지가 저장되었습니다.")
                measurement.result_image = result_image
                measurement.save()

            logger.info(f'ClientRomAPI - {manager}이 클라이언트 ({client}) 측정 기록 저장을 완료하였습니다. - {measurement.pk}')

        except Exception as err:
            logger.error(f'ClientRomAPI - {manager}이 측정 결과 처리 도중 문제가 발생하였습니다.', exc_info=True)

        return Response({}, status=200)

class ClientFinalResultAPI(APIView):
    """사용자의 최종 결과 데이터 반환"""
    
    def get(self, request):
        print(request.GET)

        finalResultModel = ClientFinalResultModel()
        
        checked_result = request.GET.getlist("checkedResultIds")

        for _id in checked_result:
            result = ClientMeasurement.objects.get(id=_id) # 해당 ID의 측정 정보

            if finalResultModel.client == None: 
                finalResultModel.setClient(result.client)

            finalResultModel.setValue(result)
        
        finalResultModel._printInfo()

        # data = FinalClientResultModelSerializer(finalResultModel).data

        result = {
            "client" : ClientSerializer(finalResultModel.client).data,
            "measurement" : finalResultModel.measurement,
        }

        return Response(result, status=200)

class ClientFinalResultModel:
    """최종 결과 데이터 모델 객체"""
    
    EXERCISE_LABEL_MAP = {
        "상지 근기능" : "upper",
        "하지 근기능" : "lower",
        "외발서기 (좌)" : "singleleg_left",
        "외발서기 (우)" : "singleleg_right",
        "심폐 기능" : "cardio",
    }

    ROM_LABEL_MAP = {
        "고관절 외전 (우)" : "rom_right_leg_abduction",
        "고관절 외전 (좌)" : "rom_left_leg_abduction",
        "어깨 외전 (우)" : "rom_right_shoulder_abduction",
        "어깨 외전 (좌)" : "rom_left_shoulder_abduction",
        "정면" : "pose_front",
        "측면" : "pose_side"
    }

    UNIT = {
        "상지 근기능" : "회",
        "하지 근기능" : "회",
        "외발서기 (좌)" : "초",
        "외발서기 (우)" : "초",
        "심폐 기능" : "회",
    }

    def __init__(self) -> None:
        self.client = None
        self.measurement = {
            "upper" : self._initExerciseValue(),
            "lower" : self._initExerciseValue(),
            "singleleg_left" : self._initExerciseValue(),
            "singleleg_right" : self._initExerciseValue(),
            "cardio" : self._initExerciseValue(),
            "rom" : self._initRomValue()
        }
    
    def _printInfo(self):
        pprint.pprint(self.client)
        pprint.pprint(self.measurement)

    def _initRomValue(self):
        return {
            "rom_right_leg_abduction" : {
                "value" : 0,
                "result_image" : ""
            },
            "rom_left_leg_abduction" : {
                "value" : 0,
                "result_image" : ""
            },
            "rom_right_shoulder_abduction" : {
                "value" : 0,
                "result_image" : ""
            },
            "rom_left_shoulder_abduction" : {
                "value" : 0,
                "result_image" : ""
            },
            "pose_front" : {
                "value" : 0,
                "result_image" : ""
            },
            "pose_side" : {
                "value" : 0,
                "result_image" : ""
            }
        }
        
    def _initExerciseValue(self):
        """운동 항목 (근기능, 심폐 기능, 상지/하지 기능) 초기 값"""
        return {
            'value' : '-',
            'grade' : '-',
        }

    def setClient(self, client):
        self.client = client
    
    def setValue(self, result):
        type = result.exercise

        if type in ClientFinalResultModel.ROM_LABEL_MAP.keys():
            data = {
                'value' : f'{result.count} 도/°',
                'result_image' : f'http://58.120.166.106:7575{result.result_image.url}' if result.result_image else None
            }
            self.setRomValue(type, data)
        else:
            data = {
                'grade' : result.grade,
                'value' : self.valueProcessing(type, result.count)
            }
            self.setExerciseValue(type, data)

    def valueProcessing(self, type, value):
        if type == '외발서기 (좌)' or type == '외발서기 (우)':
            value = int(value) / 1000

        return f'{value}{ClientFinalResultModel.UNIT[type]}'
    
    def setRomValue(self, type, data):
        self.measurement["rom"][ClientFinalResultModel.ROM_LABEL_MAP[type]] = data

    def setExerciseValue(self, type, data):
        """운동 항목 값 세팅"""
        self.measurement[ClientFinalResultModel.EXERCISE_LABEL_MAP[type]] = data
    
