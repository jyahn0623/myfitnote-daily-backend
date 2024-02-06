import datetime

from django.db import models

from account.models import Client

# upload to custom path with client name
def result_image_upload_to(instance, filename):
    return f'measurement/{instance.client.user.username}/{datetime.datetime.now().timestamp()}_{filename}'

class ClientMeasurement(models.Model):
    """사용자 측정 정보"""

    class Meta:
        ordering = ('-pk', )
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="고객")
    exercise = models.CharField(max_length=20, verbose_name="측정 항목", null=True, blank=True)
    count = models.TextField(verbose_name="횟수", null=True, blank=True)
    grade = models.TextField(verbose_name="등급", null=True, blank=True)
    raw_data = models.TextField(verbose_name="data", null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name="수행일시")
    result_image = models.ImageField(upload_to=result_image_upload_to, verbose_name="측정 결과 이미지", null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.client} | {self.count} | {self.exercise}'
