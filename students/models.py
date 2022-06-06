from django.db import models

# Create your models here.
class StudentData(models.Model):
    firstname = models.CharField(max_length=50,primary_key=True)
    lastname = models.CharField(max_length=50)
    department = models.CharField(max_length=20)
    email  =models.CharField(max_length=50)
    phoneno = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    

    def __str__(self):
        return self.firstname + self.lastname