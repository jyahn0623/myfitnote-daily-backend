from django.db import models

class Exercise(models.Model):
    """운동 및 측정 항목"""
    type_choices = (
        ('1', '측정'),
        ('2', '운동'),
    )
    name = models.CharField(max_length=100, verbose_name="항목명")
    classification = models.CharField(max_length=100, verbose_name="분류", null=True, blank=True)
    description = models.TextField(verbose_name="운동 설명", null=True, blank=True)
    type = models.CharField(max_length=1, choices=type_choices, verbose_name="항목 유형")
    thumbnail = models.ImageField(verbose_name="이미지", null=True, blank=True)
    video = models.FileField(verbose_name="영상", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 일시")

    def __str__(self) -> str:
        return self.name