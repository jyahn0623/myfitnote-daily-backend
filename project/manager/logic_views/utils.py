import json

def extrace_value_from_exercise_log(log):
    value = '-'
    data = json.loads(log.data)

    if log.type == 'TUG':
        # TUG returs time value with 's' suffix
        value = data.get('time')
        value = f'{value / 1000}'
    
    elif log.type == 'GaitSpeed':
        value = data.get('second')
        value = f'{value / 1000}'
    
    elif log.type == 'SeatDownUp':
        value = data.get('second')
        value = f'{value / 1000}'

    elif log.type == 'SITUP':
        value = data.get('count')
        value = f'{value}회'

    elif log.type == 'exercise_balance_reverse_line_test':
        value = data.get('second')
        value = f'{value / 1000}'

    elif log.type == 'exercise_balance_line_test':
        value = data.get('second')
        value = f'{value / 1000}'

    elif log.type == 'exercise_balance_test':
        value = data.get('second')
        value = f'{value / 1000}'

    elif log.type == 'SINGLE_LEGSTANCE':
        value = data.get('time')
        value = f'{value / 1000}초'
    
    elif log.type == 'WALK':
        value = data.get('count')
        value = f'{value}회'
    
    return value