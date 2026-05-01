from django.db import models
from datetime import date

class User(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Electrician', 'Electrician')
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Electrician(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Job(models.Model):
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    electrician = models.ForeignKey(Electrician, on_delete=models.CASCADE)
    deadline = models.DateField()
    status = models.CharField(max_length=20)

    # 🔥 THIS MUST EXIST
    image = models.FileField(upload_to='jobs/', null=True, blank=True)


class Task(models.Model):
    name = models.CharField(max_length=100)
    electrician = models.ForeignKey(Electrician, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)   # ✅ ADDED
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()

    def __str__(self):
        return self.name

class Report(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    report_file = models.FileField(upload_to='reports/')

    def __str__(self):
        return f"Report for {self.job.title}"