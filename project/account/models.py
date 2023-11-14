
from django.contrib.auth.models import (
        AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

from rest_framework.authtoken.models import Token

class UserManager(BaseUserManager):

    def create_user(self, phone, password):
        
        if not phone:
            raise ValueError('Users must have an phone')
        
        user = self.model(phone=phone)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password):
        user = self.create_user(
            phone=phone,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    class Meta:
        indexes = [
            models.Index(fields=['phone'])
        ]
    GENDERS = (('M', '남'), ('W', '여'))

    phone = models.CharField(max_length=15,unique=True)
    name = models.CharField(max_length=10, null=True)
    birth_date = models.DateField(null=True)
    gender = models.CharField(max_length=1, choices=GENDERS, null=True)
    height = models.CharField(max_length=3, null=True)
    weight = models.CharField(max_length=3, null=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'phone'
    

    def get_full_name(self):
        # The user is identified by their email address
        return self.name
 
    def get_short_name(self):
        # The user is identified by their email address
        return self.name
 
    def __str__(self):
        return self.phone
    
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class ExerciseLog(models.Model):
    """
    User's exerciselog

    - type:
    - user:
    - data:
    - created_at:
    """
    class Meta:
        ordering = ('-pk', )
    
    
    type = models.CharField(verbose_name="type", max_length=50, null=True)
    user = models.CharField(verbose_name="user", max_length=50, null=True)
    data = models.TextField(verbose_name="data")
    extra = models.TextField(verbose_name="extra", null=True, blank=True)
    created_at = models.DateTimeField(verbose_name="수행일시", auto_now=True)

    def get_user_name(self) -> str:
        try:
            token = Token.objects.get(key=self.user)
            return token.user.name
        except Exception as err:
            print(err)
            return ""

    def get_absolute_url(self):
        return reverse('manage:user-walk-detail', kwargs={"pk" : self.pk})

# class SitUp(models.Model):
#     user = models.CharField(verbose_name="user", max_length=50, null=True)
#     data = models.TextField(verbose_name="data")

# class EyeHandGame(models.Model):
#     user = models.CharField(verbose_name="user", max_length=50, null=True)
#     data = models.TextField(verbose_name="data")