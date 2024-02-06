from django.db import models

class Prescription(models.Model):
    """처방 Model"""
    client = models.ForeignKey('account.Client', on_delete=models.CASCADE, null=True, blank=True, verbose_name="회원")
    manager = models.ForeignKey('account.CompanyManager', on_delete=models.CASCADE, null=True, blank=True, verbose_name="담당자")
    prescription_date = models.DateField()

class PrescriptionDetail(models.Model):
    """처방 상세"""
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, null=True, blank=True, verbose_name="처방")
    exercise = models.ForeignKey('measurement.Exercise', on_delete=models.CASCADE, null=True, blank=True, verbose_name="운동 항목")
    should_do_date = models.DateField(verbose_name="수행 명령 일자", null=True, blank=True) 
    did_exercise = models.BooleanField(verbose_name="수행 여부", default=False)
    did_at = models.DateTimeField(verbose_name="수행 일시", null=True, blank=True)
    set = models.IntegerField(null=True, blank=True, verbose_name="세트")
    count = models.IntegerField(null=True, blank=True, verbose_name="횟수")
    interval = models.IntegerField(null=True, blank=True, verbose_name="간격")
    memo = models.TextField(null=True, blank=True, verbose_name="메모")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="처방 생성 일시")

    def __str__(self) -> str:
        return f'{self.exercise.name} | {self.set}세트 | {self.count}회 | {self.interval}초'

