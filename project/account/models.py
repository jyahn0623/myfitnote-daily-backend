from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

from rest_framework.authtoken.models import Token

class UserManager(BaseUserManager):

    def create_user(self, username, password, user_type):
        
        if not username:
            raise ValueError('Users must have an username')
        
        if not user_type:
            raise ValueError("User type is required!")
        
        user = self.model(username=username, user_type=user_type)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, user_type):
        user = self.create_user(
            username=username,
            password=password,
            user_type=user_type
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    USER_TYPE_CHOICES = (
            (1, 'Client'), # 기업 고객
            (2, 'Company Manager') # 기업 담당자
        )

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, null=True, blank=True, verbose_name="사용자 유형")
    username = models.CharField(max_length=150, primary_key=True, verbose_name="아이디")

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['user_type', 'password']

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    
    @property
    def user_type_label(self):
        if self.user_type == 1:
            return "고객"
        else:
            return "담당자"
    
class Company(models.Model):
    """기업"""
    class Meta:
        # set unique constraint
        constraints = [
            models.UniqueConstraint(fields=['code'], name='unique_company_code')
        ]

    name = models.CharField(max_length=20, verbose_name="기업명")
    logo = models.ImageField(null=True, blank=True, verbose_name="기업 로고")
    code = models.CharField(max_length=10, verbose_name="기업 코드", blank=True, null=True)
    primary_color = models.CharField(max_length=10, default="#00b0a6", verbose_name="기업 주요 색상 RGB")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록일시")

    def __str__(self) -> str:
        return self.name 


class CompanyManager(models.Model):
    """사용자 유형 중 기업 담당자"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="기업")
    id_number = models.CharField(max_length=20, primary_key=True, verbose_name="사번")
    phone = models.CharField(max_length=15, null=True, blank=True, verbose_name="전화번호")
    name = models.CharField(max_length=10, null=True, blank=True, verbose_name="이름")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록일시")

    def __str__(self) -> str:
        return f"{self.company.name} / {self.id_number} ({self.name})"
 

class Client(models.Model):
    """사용자 유형 중 일반 사용자"""

    class Meta:
        ordering = ('-created_at', )

    GENDER_CHOICES = (('M', '남'), ('W', '여'))
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    manager = models.ForeignKey(CompanyManager, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="담당자")
    phone = models.CharField(max_length=15, null=True, blank=True, verbose_name="전화번호")
    name = models.CharField(max_length=10, null=True, blank=True, verbose_name="이름")
    birth_date = models.DateField(null=True, blank=True, verbose_name="생년월일")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True, verbose_name="성별")
    height = models.CharField(max_length=3, null=True, blank=True, verbose_name="신장")
    weight = models.CharField(max_length=3, null=True, blank=True, verbose_name="체중")
    address = models.CharField(max_length=200, null=True, blank=True, verbose_name="주소")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록일시")

    def __str__(self) -> str:
        return f'{self.name} | {self.phone}'
  
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