from django.db import models

class DataFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'data_file'  
        

class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    active = models.BooleanField(max_length=10, default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user'  


class Company(models.Model):
    name = models.CharField(max_length=255)
    locality = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    domain = models.CharField(max_length=255) 
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=255)
    year_founded = models.IntegerField(blank=True, null=True)
    linkedin_url = models.URLField(max_length=255, blank=True, null=True)  
    size_range = models.CharField(max_length=255, blank=True, null=True)  
    current_employee_estimate = models.IntegerField(blank=True, null=True) 
    total_employee_estimate = models.IntegerField(blank=True, null=True)  

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'company'


