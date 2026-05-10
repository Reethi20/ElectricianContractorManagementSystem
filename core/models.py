from django.db import models
from datetime import date


# ================= ELECTRICIAN =================
class Electrician(models.Model):

    name = models.CharField(max_length=100)

    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name


# ================= JOB =================
class Job(models.Model):

    title = models.CharField(max_length=200)

    image = models.ImageField(
        upload_to='job_images/',
        null=True,
        blank=True
    )

    location = models.CharField(max_length=100)

    electrician = models.ForeignKey(
        Electrician,
        on_delete=models.CASCADE
    )

    deadline = models.DateField(default=date.today)

    status = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ================= REPORT =================
class Report(models.Model):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    report_file = models.FileField(
        upload_to='reports/'
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.job.title}"


# ================= USER =================
class User(models.Model):

    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Electrician', 'Electrician'),
        ('Client', 'Client')
    ]

    name = models.CharField(max_length=100)

    phone = models.CharField(max_length=15)

    email = models.EmailField()

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ================= TASK =================
class Task(models.Model):

    name = models.CharField(max_length=100)

    electrician = models.ForeignKey(
        Electrician,
        on_delete=models.CASCADE
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    status = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# ================= MATERIAL =================
class Material(models.Model):

    name = models.CharField(max_length=100)

    quantity = models.IntegerField()

    def __str__(self):
        return self.name


# ================= CLIENT REQUEST =================
class ClientRequest(models.Model):

    service_title = models.CharField(max_length=200)

    location = models.CharField(max_length=100)

    description = models.TextField()

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    electrician = models.CharField(
        max_length=100,
        default='Not Assigned'
    )

    payment_status = models.CharField(
        max_length=20,
        default='Unpaid'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.service_title