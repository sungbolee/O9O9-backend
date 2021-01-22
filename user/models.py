from django.db import models


class User(models.Model):
    username_id = models.CharField(max_length=20)
    password = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=20, null=True)
    phone_number = models.CharField(max_length=20, null=True)
    email_address = models.EmailField()

    class Meta:
        db_table = 'users'


class Allow(models.Model):
    allow_code = models.CharField(max_length=30)

    class Meta:
        db_table = 'allows'
