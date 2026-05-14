from django.db import models
from datetime import date
import uuid


# ================= USER =================

class User(models.Model):

    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Electrician', 'Electrician'),
        ('Client', 'Client')
    ]

    name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=15
    )

    email = models.EmailField(
        unique=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    password = models.CharField(
        max_length=100
    )

    def __str__(self):

        return self.name


# ================= ELECTRICIAN =================

class Electrician(models.Model):

    name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=15
    )

    def __str__(self):

        return self.name


# ================= JOB =================

class Job(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed')
    ]

    title = models.CharField(
        max_length=200
    )

    location = models.CharField(
        max_length=100
    )

    electrician = models.ForeignKey(
        Electrician,
        on_delete=models.CASCADE
    )

    deadline = models.DateField(
        default=date.today
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    image = models.FileField(
        upload_to='job_images/',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.title


# ================= TASK =================

class Task(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ]

    name = models.CharField(
        max_length=100
    )

    electrician = models.ForeignKey(
        Electrician,
        on_delete=models.CASCADE
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):

        return self.name


# ================= MATERIAL =================

class Material(models.Model):

    PAYMENT_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid')
    ]

    name = models.CharField(
        max_length=100
    )

    quantity = models.IntegerField()

    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='Pending'
    )

    def __str__(self):

        return self.name


# ================= CLIENT REQUEST =================

class ClientRequest(models.Model):

    STATUS_CHOICES = [

        ('Pending', 'Pending'),

        ('In Progress', 'In Progress'),

        ('Completed', 'Completed')

    ]

    client = models.ForeignKey(

        User,

        on_delete=models.CASCADE,

        null=True,

        blank=True

    )

    service_title = models.CharField(
        max_length=200
    )

    location = models.CharField(
        max_length=100
    )

    description = models.TextField()

    status = models.CharField(

        max_length=20,

        choices=STATUS_CHOICES,

        default='Pending'

    )

    electrician = models.CharField(

        max_length=100,

        default='Not Assigned'

    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.service_title


# ================= REPORT =================

class Report(models.Model):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    report_file = models.FileField(
        upload_to='reports/'
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"Report for {self.job.title}"


# ================= PAYMENT =================

class Payment(models.Model):

    payer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payer_payments'
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='receiver_payments'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_type = models.CharField(
        max_length=100
    )

    payment_method = models.CharField(
        max_length=100
    )

    status = models.CharField(
        max_length=50,
        default='Pending'
    )

    # ADD THESE

    transaction_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.payer} -> {self.receiver}"
    
