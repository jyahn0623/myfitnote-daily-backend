import datetime
import logging

from django.db import transaction

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action

from prescription.api.serializers import *
from prescription.models import Prescription, PrescriptionDetail

from measurement.models import *
from client.models import *

logger = logging.getLogger('application')

class PrescriptionViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )

    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

    def retrieve(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        data['prescription_details'] = instance.prescriptiondetail_set.all().values()

        return Response(data)

    # Create make prescription
    @action(methods=['post'], detail=False)
    def make_prescription(self, request):
        """처방전 발급"""
        checked_result = request.GET.getlist("checkedResultIds")
        message = ""
        client = None

        has_walk = False
        exercise_map = {}
        

        # Get user from client measurement => TODO: need to get client from request header or body
        for checked_id in checked_result:
            result = ClientMeasurement.objects.get(id=checked_id)

            if client is None:
                client = result.client

            if result.exercise == '심폐 기능':
                # 걷기 운동 수행했던 횟수의 10%를 횟수로 지정
                # 220 - 나이 * 0.65 = 목표 심박수
                has_walk = True
                exercise_map[result.exercise] = int(result.count) * 0.9

        if not has_walk:
            return Response({"success": False, "message": "걷기 측정 결과를 선택해 주셔야 합니다."}, status=200)
            

        # if prescription is already exist which made by today
        if Prescription.objects.filter(client=client, 
                                       prescription_date=datetime.date.today()).exists():
            message = "이미 오늘 처방전을 발급받았습니다."
            return Response({"success": False, "message": message}, status=200)

        with transaction.atomic():   
            # 처방전 생성
            prescription = Prescription.objects.create(
                client=result.client,
                manager=request.user.companymanager,
                prescription_date=datetime.date.today()
            )

            # 처방 항목 생성
            detail = PrescriptionDetail.objects.create(
                prescription=prescription,
                exercise=Exercise.objects.get(name='걷기'),
                should_do_date=datetime.date.today(),
                set=1,
                count=exercise_map.get("심폐 기능"),
                interval=10,
            )

            message = "처방전을 성공적으로 발급하였습니다."

            # 임시 처방 내역
            message += "\n\n처방 프로그램 내역\n"
            message += f"{detail.exercise.name} | {detail.set}세트 | {detail.count}회 | {detail.interval}초"

        return Response({"success": True, "message": message}, status=200)

    @action(methods=['get'], detail=False)
    def get_today_prescription(self, request):
        today = datetime.date.today()
        logger.info(f"처방전 요청 | {request.user.client}")
        prescription = Prescription.objects.filter(client=request.user.client).last()
        logger.info(f"처방전 | {prescription}")
        # if prescription's created_at is over 28 days, then return None
        if (today - prescription.prescription_date).days > 28:
            logger.info(f"처방전 만료 | {prescription}")
            return Response({}, status=200)
        
        logger.info("처방전 조회 성공")
        # Get client's today prescription
        prescription = PrescriptionDetail.objects.get(prescription=prescription)
                                                    #   should_do_date=today)
        print(prescription)
        data = PrescriptionDetailSerializer(prescription).data
        print(data)
        return Response(data, status=200)
    
    @action(methods=['get'], detail=False)
    def finish_prescription_exercise(self, request):
        """처방전에 할당되어 있는 운동 종료 시"""
        prescription = Prescription.objects.filter(client=request.user.client).last()