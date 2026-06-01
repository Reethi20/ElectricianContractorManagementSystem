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

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    password = models.CharField(max_length=100)

    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


# ================= ELECTRICIAN =================

class Electrician(models.Model):

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Working', 'Working'),
        ('Leave', 'On Leave')
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    image = models.ImageField(
        upload_to='electricians/',
        blank=True,
        null=True
    )

    rating = models.FloatField(default=0)
    total_reviews = models.IntegerField(default=0)

    availability = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Available'
    )

    service_area_pincode = models.CharField(
        max_length=6,
        blank=True,
        default=''
    )

    def __str__(self):
        return self.name


# ================= JOB =================

class Job(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed')
    ]

    title = models.CharField(max_length=200)

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
        blank=True,
        null=True
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

    name = models.CharField(max_length=100)

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

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='materials'
    )

    name = models.CharField(max_length=100)
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
        blank=True,
        null=True
    )

    service_title = models.CharField(
        max_length=200
    )

    location = models.CharField(
        max_length=100
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        default=''
    )

    pincode = models.CharField(
        max_length=6,
        blank=True,
        default=''
    )

    description = models.TextField()

    request_image = models.ImageField(
        upload_to='client_requests/',
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    electrician = models.CharField(
        max_length=100,
        default='Not Assigned'
    )

    quoted_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    advance_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    is_quote_approved = models.BooleanField(
        default=False
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

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded')
    ]

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

    transaction_id = models.CharField(
        max_length=255,
        unique=True,
        default=uuid.uuid4
    )

    invoice_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return str(self.transaction_id)


# ================= OTP =================

class OTP(models.Model):

    email = models.EmailField()

    otp = models.CharField(
        max_length=6
    )

    is_used = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.email


# ================= FAQ =================

class FAQ(models.Model):

    question = models.CharField(
        max_length=500
    )

    answer = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.question


# ================= NOTIFICATION =================

class Notification(models.Model):

    TYPE_CHOICES = [
        ('Payment', 'Payment'),
        ('Job', 'Job'),
        ('Request', 'Request'),
        ('Review', 'Review')
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    notification_type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES
    )

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title

# ================= REVIEW =================

class Review(models.Model):

    electrician = models.ForeignKey(
        Electrician,
        on_delete=models.CASCADE
    )

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField()

    review = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = [
        'electrician',
        'client'
    ]

    def __str__(self):
        return str(self.rating)


# ================= SERVICE OTP =================

class ServiceOTP(models.Model):

    client_request = models.ForeignKey(
        ClientRequest,
        on_delete=models.CASCADE
    )

    generated_by = models.ForeignKey(
        Electrician,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    otp = models.CharField(
        max_length=6
    )

    is_verified = models.BooleanField(
        default=False
    )

    verified_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.otp
