from django.contrib import admin

from account.models import *

admin.site.register(User)
admin.site.register(ExerciseLog)
admin.site.register(Company)
admin.site.register(CompanyManager)
admin.site.register(Client)