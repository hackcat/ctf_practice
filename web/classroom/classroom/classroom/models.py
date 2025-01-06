from django.db import models

class Student(models.Model):
    name = models.CharField('', max_length=64, unique=True)
    no = models.CharField('', max_length=12, unique=True)
    passkey = models.CharField('', max_length=32)
    group = models.ForeignKey('Group', verbose_name='', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = ''
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField('', max_length=64)
    information = models.TextField('')
    secret = models.CharField('', max_length=128)
    created_time = models.DateTimeField('', auto_now_add=True)

    class Meta:
        verbose_name = ''
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
