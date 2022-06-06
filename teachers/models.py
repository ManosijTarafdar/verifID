from django.db import models

# Create your models here.
class TeacherData(models.Model):
    collegeid = models.CharField(max_length=30,primary_key=True)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    designation = models.CharField(max_length=20)
    department = models.CharField(max_length=50)
    email  =models.CharField(max_length=50)
    phoneno = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    deviceid = models.CharField(max_length=50,null=False)
    

    def __str__(self):
        return self.collegeid
