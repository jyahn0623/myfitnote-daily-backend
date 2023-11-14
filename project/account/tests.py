import pprint
import unittest
import time
import json
import collections 

from django.test import TestCase

from account.models import *
from account.utils import *

from manager.logic_views.utils import extrace_value_from_exercise_log

class NoMercyDummeyDataTestCase(unittest.TestCase):
    def test_create_dummy_data(self):
        DUMMY_COUNT = 1000000
        print(self.__str__())
        start_time = time.time()
        create_response = User.objects.bulk_create([
            User(phone=idx) for idx in range(DUMMY_COUNT)
        ])
        print('end bulk_create: ', time.time() - start_time)

    def test_delete_dummy_data(self):
        User.objects.all().delete()
        
    def test_select_form_user(self):
        user = User.objects.filter(phone__gt=100, phone__lt=200)
        print(user.explain(), end='\n\n')
        user = User.objects.filter(phone=100)
        print(user.explain())

        """
        we can choose index method proper,
        in so fucking much data-> Sequencial Scan
        in neither so fucking much nor fukcing less, -> Bitmap Scan
        in so small much data -> Index Scan
        Bitmap Heap Scan on account_user  (cost=5311.91..14305.90 rows=109999 width=107)
            Recheck Cond: (((phone)::text > '100'::text) AND ((phone)::text < '200'::text))
            ->  Bitmap Index Scan on account_user_phone_key  (cost=0.00..5284.41 rows=109999 width=0)
                    Index Cond: (((phone)::text > '100'::text) AND ((phone)::text < '200'::text))

        Index Scan using account_user_phone_1704cc19_like on account_user  (cost=0.42..8.44 rows=1 width=107)
            Index Cond: ((phone)::text = '100'::text)

        After add index in models.py
        Bitmap Heap Scan on account_user  (cost=2335.91..11329.90 rows=109999 width=107)
            Recheck Cond: (((phone)::text > '100'::text) AND ((phone)::text < '200'::text))
            ->  Bitmap Index Scan on account_use_phone_664a69_idx  (cost=0.00..2308.41 rows=109999 width=0)
                    Index Cond: (((phone)::text > '100'::text) AND ((phone)::text < '200'::text))

        Index Scan using account_user_phone_1704cc19_like on account_user  (cost=0.42..8.44 rows=1 width=107)
            Index Cond: ((phone)::text = '100'::text)
        """

class WalkTestCase(unittest.TestCase):
    def test_walk_data_type(self):
        walk = Walk.objects.first()
        walk_data = walk.data
        walk_data = data_to_dict(walk_data)
        self.assertTrue(isinstance(walk_data, dict))

class ExerciseSerieseTestCase(unittest.TestCase):
    def test_get_series_data(self):
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
                'date' : d.created_at,
                'value' : extrace_value_from_exercise_log(d)
            })
        
        pprint.pprint(data_dict)

        

    