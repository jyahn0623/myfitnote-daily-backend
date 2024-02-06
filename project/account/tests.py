import pprint
import unittest
import time
import json
import collections 

from django.test import TestCase
from django.contrib.auth import get_user_model

from account.models import *
from account.utils import *
from account.api.serializers import *
from account.selectors import *

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

class ModelTestCase(TestCase):

    def setUp(self):
        # Create a sample user for testing
        self.user = get_user_model().objects.create_user(
            username='123456789',
            password='testpassword',
            user_type=1
        )

        # Create a sample company for testing
        self.company = Company.objects.create(
            name='Test Company',
            logo=None,
            primary_color='#00b0a6'
        )

        # Create a sample company manager for testing
        self.company_manager = CompanyManager.objects.create(
            user=self.user,
            company=self.company,
            id_number='12345',
            phone='987654321',
            name='Manager Name'
        )

        # Create a sample client for testing
        self.client_user = Client.objects.create(
            user=self.user,
            manager=self.company_manager,
            phone='111222333',
            name='Client Name',
            birth_date='2000-01-01',
            gender='M',
            height='180',
            weight='70',
            address='Test Address'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, '123456789')
        self.assertTrue(self.user.check_password('testpassword'))

    def test_company_creation(self):
        self.assertEqual(self.company.name, 'Test Company')
        self.assertEqual(self.company.primary_color, '#00b0a6')

    def test_company_manager_creation(self):
        self.assertEqual(self.company_manager.company, self.company)
        self.assertEqual(self.company_manager.id_number, '12345')
        self.assertEqual(self.company_manager.phone, '987654321')
        self.assertEqual(self.company_manager.name, 'Manager Name')

    def test_client_creation(self):
        self.assertEqual(self.client_user.manager, self.company_manager)
        self.assertEqual(self.client_user.phone, '111222333')
        self.assertEqual(self.client_user.name, 'Client Name')
        self.assertEqual(str(self.client_user.birth_date), '2000-01-01')
        self.assertEqual(self.client_user.gender, 'M')
        self.assertEqual(self.client_user.height, '180')
        self.assertEqual(self.client_user.weight, '70')
        self.assertEqual(self.client_user.address, 'Test Address')
        
    def test_client_manager_drf(self):
        
        manager = CompanyManager.objects.first()
        data = CompanyManagerSerializer(manager).data

        print(data)

class ClientTestCase(unittest.TestCase):

    def test_create_dummy_client(self):

        name = [
            "민준",
            "서준",
            "도윤",
            "예준",
            "시우",
            "하준",
            "지호",
            "주원",
            "지후",
            "준우",
            "준서",
            "도현",
        ]
        
        for n in name:
            client = Client.objects.first()
            client.pk = None
            client.name = n
            client.save()

        

        print(client)


class UserSelectorTestCase(unittest.TestCase):
    def setUp(self):
        self.selector = UserSelector()
        self.company = Company.objects.first()

    def test_get_user_by_company(self):
        users = self.selector.get_user_by_company(self.company)
        print(users) 