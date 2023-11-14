import tempfile
import os
import json

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.conf import settings

from account.api.views import (
    UserAPI,
    UserWalkAPI
)
from account.models import *
from account.utils import *

def index(request: HttpRequest) -> HttpResponse: 
    return render(request, 'manager/index.html')

def user_inquiry(request: HttpRequest) -> HttpResponse:
    api = UserAPI()
    response = api.list(request)
    return render(request, 'manager/user/index.html', {
        'users' : response.data['response']
    })

def user_walk_inquiry(request: HttpRequest) -> HttpResponse:
    data = ExerciseLog.objects.filter(type='WALK')

    return render(request, 'manager/walk/index.html', {
        'data' : data
    })

def user_situp_inquiry(request: HttpRequest) -> HttpResponse:
    data = ExerciseLog.objects.filter(type='SITUP')

    return render(request, 'manager/situp/index.html', {
        'data' : data
    })

def user_eyehand_inquiry(request: HttpRequest) -> HttpResponse:
    data = ExerciseLog.objects.filter(type='EYEHAND')

    return render(request, 'manager/eyehand/index.html', {
        'data' : data
    })

def user_data_detail(request, pk) -> HttpResponse:
    log = get_object_or_404(ExerciseLog, pk=pk)
    _type = log.type
    template_name = ""
    data = json.loads(log.data)
    if _type == 'WALK':
        data['logData'] = sorted(data['logData'].items(), key=lambda x : int(x[0]))
        template_name = 'manager/walk/detail.html'

    elif _type == 'SITUP':
        template_name = 'manager/situp/detail.html'
        data['logData'] = sorted(data.get('logData').items(), key=lambda x : int(x[0]))
        duplication_check_dict = {}
        all_data = {}
        use_first_timestamp_as_standard = False
        _time, _last_time = 0, 0
        for timestamp, _data in data['logData']:
            if (_data[0], _data[1]) not in duplication_check_dict:
                if not use_first_timestamp_as_standard:
                    use_first_timestamp_as_standard = True
                    _time = 0
                else:
                    interval_time = int(timestamp) - int(_last_time)
                    _time += interval_time
                # this is for removal duplication data.
                # e.g) when action is stand, there are multipe data, but we need only first thing.
                duplication_check_dict[(_data[0], _data[1])] = True
                processed_list = [value for value in _data]
                processed_list[1] = '서기' if processed_list[1] == 1.0 else '앉기'
                all_data[_time] = processed_list
                _last_time = timestamp 
        data['logData'] = all_data

    elif _type == 'EYEHAND':
        clicked_time = data.get('clickedTime')
        template_name = 'manager/eyehand/detail.html'
        time_interval = [0] + [ clicked_time[i+1] - clicked_time[i] \
                                for i in range(len(clicked_time)-1)]
        data['processed_data'] = tuple(zip(data.get('clickedBall'),
                                           clicked_time,
                                           time_interval))
        data['showBalls_format'] = '-'.join([ 'G' if ball == 0 else 'R' 
                                             for ball in data.get('showBalls')])
    return render(request, template_name, {
        'data' : data
    })


def analysis_pose(request: HttpRequest) -> HttpResponse:

    if request.method == 'POST':
        import mediapipe as mp
        import cv2
        import pandas as pd

        mp_holistic = mp.solutions.holistic

        header = ['time']
        for lm in mp_holistic.PoseLandmark:
            header.append(f'{lm.name} x')
            header.append(f'{lm.name} y')
            header.append(f'{lm.name} z')

        pose = mp.solutions.pose.Pose(
            static_image_mode=False, 
            min_detection_confidence=0.5, 
            min_tracking_confidence=0.5)

        pose_data = []
        _file = request.FILES.get('file')
        with tempfile.NamedTemporaryFile(delete=False) as f:
            for chunk in _file.chunks():
                f.write(chunk)
        
        file_name = f.name.split('/')[-1]
        webcam = cv2.VideoCapture(f.name) 

        width = int(webcam.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(webcam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(webcam.get(cv2.CAP_PROP_FPS))

        fourcc = cv2.VideoWriter_fourcc(*'VP80')
        processed_file_path = os.path.join(settings.MEDIA_ROOT, f'{file_name}.webm')
        processed_video = cv2.VideoWriter(processed_file_path, fourcc, fps, (width, height))

        while webcam.isOpened():
            ck, frame = webcam.read()
            data = []
            if not ck:
                break

            # get timestamp a frame
            timestamp = webcam.get(cv2.CAP_PROP_POS_MSEC)
            data.append(round(timestamp, 2))
            
            results = pose.process(frame)
            if results:
                for lm in mp_holistic.PoseLandmark:
                    # print(dir(results.pose_landmarks)/)
                    # lm.name, lm.value
                    if results.pose_landmarks:
                        data.append(round(results.pose_landmarks.landmark[lm].x, 2))
                        data.append(round(results.pose_landmarks.landmark[lm].y, 2))
                        data.append(round(results.pose_landmarks.landmark[lm].z, 2))
                      
                mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)

            pose_data.append(data)
            processed_video.write(frame)
            

        webcam.release()
        processed_video.release()

        pd.DataFrame(pose_data).to_csv(os.path.join(settings.MEDIA_ROOT, 
                                      f'{file_name}.csv'),
                                      header=header)

        os.unlink(f.name)
        print("Processed is done!")

        return JsonResponse({
            'processed_file' : f'/media/{file_name}.webm',
            'row_data_file' : f'/media/{file_name}.csv',
            'pose_data' : json.dumps(pose_data),
            'table_header' : json.dumps(header)
        })

    context = {
        "title" : "동작 분석",
        "sub_title" : "영상을 기반으로 동작을 분석해 보세요."
    }
    return render(request, 'manager/analysis/pose/index.html', context)