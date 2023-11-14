"""대교 Logic

Created by Juyoung Ahn
"""
import json

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q


from account.models import ExerciseLog, User

class SelectorBase:
    user_model = User

    def get_users_by_include_name(self, name):
        exception_query = Q(name='양용우')
        
        return self.user_model.objects.filter(Q(phone__startswith=name) | exception_query)
    
    def queryset_order_by(self, queryset, order_by_condition):
        return queryset.order_by(order_by_condition)

class ExerciseLogSelector(SelectorBase):
    model = ExerciseLog

    def process_logdata_by_exercise_type(self, log):
        """운동 타입별 데이터 처리"""
        print(log.type)

        value = ''
        data_to_json = json.loads(log.data)

        if log.type == 'TUG':
            # TUG returs time value with 's' suffix
            value = data_to_json.get('time')
            value = f'{value / 1000}s'
        
        elif log.type == 'GaitSpeed':
            value = data_to_json.get('second')
            value = f'{value / 1000}s'
        
        elif log.type == 'SeatDownUp':
            value = data_to_json.get('second')
            value = f'{value / 1000}s'

        elif log.type == 'SITUP':
            value = data_to_json.get('second')
            value = f'{value / 1000}s'

        elif log.type == 'exercise_balance_reverse_line_test':
            value = data_to_json.get('second')
            value = f'{value / 1000}s'

        elif log.type == 'exercise_balance_line_test':
            value = data_to_json.get('second')
            value = f'{value / 1000}s'

        elif log.type == 'exercise_balance_test':
            value = data_to_json.get('second')
            value = f'{value / 1000}s'

        elif log.type == 'SINGLE_LEGSTANCE':
            value = data_to_json.get('time')
            value = f'{value / 1000}s'

        return value


    def get_logdata_by_token(self, token):
        return self.model.objects.filter(user=token)

    def get_logdata_by_users(self, users) -> dict:
        data = {}
        for user in users: 
            token = user.auth_token.key
            logdata = self.get_logdata_by_token(token)
            # Store user data with dict
            data[user.phone] = {log.type : self.process_logdata_by_exercise_type(log) \
                                for log in logdata}
            data[user.phone]['name'] = user.name
            data[user.phone]['date'] = logdata.last().created_at \
                                       if logdata \
                                       else '-'

        return data
    
def index(request):
    selector = ExerciseLogSelector()
    users = selector.get_users_by_include_name('0808')
    users = selector.queryset_order_by(users, '-pk')
    data = selector.get_logdata_by_users(users)
    
    return render(request, 'manager/center/daekyo/index.html', {
        'data' : data
    })