from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from datetime import date
import re
import random
import json
from .models import *
from .forms import JobForm, ReportForm
from django.conf import settings
from django.core.mail import send_mail
from decimal import Decimal

# ================= ROLE CHECK =================
def is_admin(request):
    return request.session.get('role') == "Admin"

def is_electrician(request):
    return request.session.get('role') == "Electrician"

def is_client(request):
    return request.session.get('role') == "Client"

# ================= LOGIN CHECK =================
def check_login(request):
    if not request.session.get('user_id'):
        return redirect('/login/')


def pincode_from_text(text):
    match = re.search(r'\b\d{6}\b', text or '')
    return match.group(0) if match else ''


def request_workflow_status(client_request):
    if client_request.status == "Completed":
        return "Completed"
    if ServiceOTP.objects.filter(
        client_request=client_request,
        is_verified=True
    ).exists():
        return "Work In Progress"
    if client_request.electrician != "Not Assigned":
        return "Electrician Assigned"
    if client_request.is_quote_approved:
        return "Advance Paid"
    if client_request.quoted_amount and client_request.quoted_amount > 0:
        return "Quotation Sent"
    return "Request Submitted"


def attach_request_workflow(requests_data):
    for item in requests_data:
        item.workflow_status = request_workflow_status(item)
        item.display_pincode = item.pincode or pincode_from_text(item.location)
        item.display_address = item.address or item.location
        latest_otp = ServiceOTP.objects.filter(
            client_request=item
        ).order_by('-id').first()
        item.latest_otp = latest_otp
        item.remaining_balance = max(
            item.quoted_amount - item.advance_amount,
            Decimal('0')
        )
    return requests_data


def sync_job_completion(job):
    if not job:
        return
    task_count = Task.objects.filter(job=job).count()
    completed_count = Task.objects.filter(
        job=job,
        status="Completed"
    ).count()
    if task_count and task_count == completed_count:
        job.status = "Completed"
        job.save()

# ================= HOME =================
def home(request):
    return render(request, 'index.html', {
        'total_electricians': Electrician.objects.count(),
        'total_jobs': Job.objects.count(),
        'total_tasks': Task.objects.count(),
        'total_payments': Payment.objects.count(),
    })

# ================= REGISTER =================
def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        role = request.POST.get('role')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # EMPTY FIELD CHECK
        if not all([name, phone, email, role, password, confirm_password]):
            return render(request, 'register.html', {
                'error': 'All fields are required'
            })

        if password != confirm_password:
            return render(request, 'register.html', {
                'error': 'Passwords do not match'
            })

        # PASSWORD LENGTH CHECK
        if len(password) < 8:
            return render(request, 'register.html', {
                'error': 'Password must be at least 8 characters'
            })

        # PASSWORD VALIDATION
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).+$'
        if not re.match(pattern, password):
            return render(request, 'register.html', {
                'error': 'Password must contain uppercase, lowercase, number and special character'
            })

        # EMAIL EXISTS CHECK
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {
                'error': 'Email already exists'
            })

        # CREATE USER
        User.objects.create(
            name=name,
            phone=phone,
            email=email,
            role=role,
            password=make_password(password)
        )

        # AUTO CREATE ELECTRICIAN

        if role == "Electrician":
            if not Electrician.objects.filter(
                phone=phone
            ).exists():
                Electrician.objects.create(
                    name=name,
                    phone=phone
                )
        return redirect('/login/')
    return render(request, 'register.html')

# ================= LOGIN =================
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.filter(
            email=email
        ).first()
        if user and check_password(
            password,
            user.password
        ):
            # SESSION
            request.session['user_id'] = user.id
            request.session['role'] = user.role
            request.session['name'] = user.name
            request.session['phone'] = user.phone

            # ROLE BASED REDIRECT
            if user.role == "Admin":
                return redirect('/dashboard/')
            elif user.role == "Electrician":
                return redirect('/tasks/')
            elif user.role == "Client":
                return redirect('/client-dashboard/')
        return render(request, 'login.html', {
            'error': 'Invalid email or password'
        })
    return render(request, 'login.html')

# ================= LOGOUT =================
def logout(request):
    request.session.flush()
    return redirect('/login/')
# ================= FORGOT PASSWORD =================
def forgot_password(request):

    if request.method == "POST":

        # ================= SEND OTP =================

        if "send_otp" in request.POST:

            email = request.POST.get("email")

            user = User.objects.filter(
                email=email
            ).first()

            if not user:

                return render(
                    request,
                    "forgot_password.html",
                    {
                        "error": "Email not found"
                    }
                )

            otp = str(
                random.randint(
                    100000,
                    999999
                )
            )

            OTP.objects.create(
                email=email,
                otp=otp
            )

            try:

                message = f"""

    Dear User,

    We received a request to reset the password for your Electrical Contractor Management System (ECMS) account.

    Your One-Time Password (OTP) is:

    {otp}

    This OTP is valid for 10 minutes and can be used only once.

    If you did not request a password reset, please ignore this email.

    Regards,
    ECMS Support Team
    Electrical Contractor Management System
    """
                send_mail(
                    "ECMS Password Reset Request",
                    message,
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False
                )

            except Exception as e:

                return render(
                    request,
                    "forgot_password.html",
                    {
                        "error": f"Email Error : {e}"
                    }
                )

            return render(
                request,
                "forgot_password.html",
                {
                    "success": "OTP sent successfully",
                    "email": email
                }
            )

        # ================= VERIFY OTP =================

        elif "verify_otp" in request.POST:

            email = request.POST.get("email")

            otp = request.POST.get("otp")

            otp_record = OTP.objects.filter(

                email=email,

                otp=otp,

                is_used=False

            ).first()

            if otp_record:

                return render(

                    request,

                    "forgot_password.html",

                    {

                        "email": email,

                        "otp_verified": True,

                        "success":
                        "OTP verified successfully"

                    }

                )

            return render(

                request,

                "forgot_password.html",

                {

                    "email": email,

                    "error":
                    "Invalid OTP"

                }

            )

        # ================= RESET PASSWORD =================

        elif "reset_password" in request.POST:

            email = request.POST.get("email")

            otp = request.POST.get("otp")

            password = request.POST.get("password")

            confirm_password = request.POST.get(
                "confirm_password"
            )

            if password != confirm_password:

                return render(
                    request,
                    "forgot_password.html",
                    {
                        "error": "Passwords do not match",
                        "email": email
                    }
                )

            otp_record = OTP.objects.filter(
                email=email,
                otp=otp,
                is_used=False
            ).first()

            if not otp_record:

                return render(
                    request,
                    "forgot_password.html",
                    {
                        "error": "Invalid OTP",
                        "email": email
                    }
                )

            user = User.objects.get(
                email=email
            )

            user.password = make_password(
                password
            )

            user.save()

            otp_record.is_used = True

            otp_record.save()

            return redirect("/login/")

    return render(
        request,
        "forgot_password.html"
    )

# ================= DASHBOARD =================
def dashboard(request):
    if check_login(request):
        return check_login(request)
    # ADMIN ONLY
    if not is_admin(request):
        if is_client(request):
            return redirect('/client-dashboard/')
        return redirect('/tasks/')
    tasks = Task.objects.all().order_by('-id')[:5]
    payments = Payment.objects.all().order_by('-id')[:5]
    requests_data = ClientRequest.objects.all().order_by('-id')[:5]
    attach_request_workflow(requests_data)
    return render(request, 'dashboard.html', {
        'total_electricians': Electrician.objects.count(),
        'total_jobs': Job.objects.count(),
        'pending_tasks': Task.objects.filter(
            status="Pending"
        ).count(),
        'completed_tasks': Task.objects.filter(
            status="Completed"
        ).count(),
        'inprogress_tasks': Task.objects.filter(
            status="In Progress"
        ).count(),
        'total_payments': Payment.objects.count(),
        'tasks': tasks,
        'payments': payments,
        'requests_data': requests_data
    })

# ================= CLIENT DASHBOARD =================
def client_dashboard(request):
    if check_login(request):
        return check_login(request)
    # CLIENT ONLY
    if not is_client(request):
        return redirect('/dashboard/')
    requests_data = ClientRequest.objects.filter(
        client_id=request.session['user_id']
    )
    attach_request_workflow(requests_data)
    return render(request, 'client_dashboard.html', {
        'requests_data': requests_data,
        'total_requests': requests_data.count(),
        'completed_requests': requests_data.filter(
            status='Completed'
        ).count(),
        'pending_requests': requests_data.filter(
            status='Pending'
        ).count(),
    })

# ================= MY REQUESTS =================
def my_requests(request):
    if check_login(request):
        return check_login(request)
    # CLIENT ONLY
    if not is_client(request):
        return redirect('/dashboard/')
    client = User.objects.get(
        id=request.session['user_id']
    )

    if request.method == 'POST':
        if request.POST.get('action') == 'approve_quote':
            ClientRequest.objects.filter(
                id=request.POST.get('id'),
                client=client
            ).update(is_quote_approved=True)
            return redirect('/my-requests/')

        ClientRequest.objects.create(
            client=client,
            service_title=request.POST.get(
                'service_title'
            ),
            # Location matching can be extended using Google Maps API in future versions.
            location=request.POST.get('address'),
            address=request.POST.get('address'),
            pincode=request.POST.get('pincode'),
            description=request.POST.get(
                'description'
            ),
        )
        return redirect('/my-requests/')
    requests_data = ClientRequest.objects.filter(
        client=client
    ).order_by('-id')
    attach_request_workflow(requests_data)
    return render(request, 'my_requests.html', {
        'requests_data': requests_data,
        'total_requests': requests_data.count(),
        'completed_requests': requests_data.filter(
            status='Completed'
        ).count(),
        'pending_requests': requests_data.filter(
            status='Pending'
        ).count(),
    })

# ================= ELECTRICIANS =================

def electricians(request):

    if check_login(request):

        return check_login(request)

    # ADMIN ONLY

    if not is_admin(request):

        return redirect('/dashboard/')

    electricians_list = Electrician.objects.all().order_by('-id')

    search = request.GET.get('search')

    if search:

        electricians_list = electricians_list.filter(

            name__icontains=search

        )

    # ================= ADD / UPDATE =================

    if request.method == 'POST':

        action = request.POST.get('action')

        # ================= ADD =================

        if action == "add":

            name = request.POST.get('name')

            phone = request.POST.get('phone')

            # PREVENT DUPLICATE PHONE

            if not Electrician.objects.filter(
                phone=phone
            ).exists():

                # CREATE ELECTRICIAN
                image = request.FILES.get(
                    'image'
                )

                Electrician.objects.create(

                    name=name,

                    phone=phone,

                    image=image,

                    service_area_pincode=request.POST.get(
                        'service_area_pincode'
                    ) or ''

                )

                # CREATE USER ACCOUNT

                if not User.objects.filter(
                    phone=phone
                ).exists():

                    User.objects.create(

                        name=name,

                        phone=phone,

                        email=f"{phone}@ecms.com",

                        role="Electrician",

                        password=make_password(
                            "Electric@123"
                        )

                    )

        # ================= UPDATE =================

        elif action == "update":

            electrician = Electrician.objects.get(

                id=request.POST.get('id')

            )

            old_phone = electrician.phone

            electrician.name = request.POST.get(
                'name'
            )

            electrician.phone = request.POST.get(
                'phone'
            )
            if request.FILES.get('image'):
                electrician.image = request.FILES.get('image')

            if request.POST.get('availability'):
                electrician.availability = request.POST.get('availability')

            electrician.service_area_pincode = request.POST.get(
                'service_area_pincode'
            ) or ''

            electrician.save()

            # UPDATE USER ACCOUNT ALSO

            user = User.objects.filter(
                phone=old_phone,
                role="Electrician"
            ).first()

            if user:

                user.name = electrician.name

                user.phone = electrician.phone

                user.email = (
                    f"{electrician.phone}@ecms.com"
                )

                user.save()

        return redirect('/electricians/')

    return render(request, 'electricians.html', {

        'electricians': electricians_list

    })


# ================= DELETE ELECTRICIAN =================

def delete_electrician(request, id):

    if check_login(request):

        return check_login(request)

    # ADMIN ONLY

    if not is_admin(request):

        return redirect('/dashboard/')

    electrician = Electrician.objects.filter(
        id=id
    ).first()

    if electrician:

        # DELETE USER ACCOUNT ALSO

        User.objects.filter(
            phone=electrician.phone,
            role="Electrician"
        ).delete()

        electrician.delete()

    return redirect('/electricians/')
# ================= JOBS =================

def jobs(request):

    if check_login(request):

        return check_login(request)

    # ================= ROLE BASED JOBS =================

    if is_admin(request):

        jobs_list = Job.objects.all().order_by('-id')

    elif is_electrician(request):

        jobs_list = Job.objects.filter(

            electrician__phone=request.session['phone']

        ).order_by('-id')

    else:

        jobs_list = Job.objects.none()

    # ================= SEARCH =================

    search = request.GET.get('search')

    if search:

        jobs_list = jobs_list.filter(

            title__icontains=search

        )

    # ================= ADD / UPDATE =================

    if request.method == 'POST':

        # ADMIN ONLY

        if not is_admin(request):

            return redirect('/jobs/')

        action = request.POST.get('action')

        # ================= ADD =================

        if action == "add":

            Job.objects.create(

                title=request.POST.get('title'),

                location=request.POST.get(
                    'location'
                ),

                electrician_id=request.POST.get(
                    'electrician'
                ),

                deadline=request.POST.get(
                    'deadline'
                ),

                status=request.POST.get(
                    'status'
                ) or "Pending",

                image=request.FILES.get(
                    'image'
                )

            )

        # ================= UPDATE =================

        elif action == "update":

            job = Job.objects.get(

                id=request.POST.get('id')

            )

            job.title = request.POST.get(
                'title'
            )

            job.location = request.POST.get(
                'location'
            )

            job.electrician_id = request.POST.get(
                'electrician'
            )

            job.deadline = request.POST.get(
                'deadline'
            )

            job.status = request.POST.get(
                'status'
            ) or "Pending"

            if request.FILES.get('image'):

                job.image = request.FILES.get(
                    'image'
                )

            job.save()

        return redirect('/jobs/')

    return render(request, 'jobs.html', {

        'jobs': jobs_list,

        'electricians': Electrician.objects.all()

    })


# ================= DELETE JOB =================

def delete_job(request, id):

    if check_login(request):

        return check_login(request)

    # ADMIN ONLY

    if not is_admin(request):

        return redirect('/dashboard/')

    Job.objects.filter(

        id=id

    ).delete()

    return redirect('/jobs/')

# ================= TASKS =================

def tasks(request):

    if check_login(request):

        return check_login(request)

    # ================= ROLE BASED TASKS =================

    if is_admin(request):

        tasks_list = Task.objects.all().order_by('-id')
        assigned_requests = ClientRequest.objects.none()

    elif is_electrician(request):

        tasks_list = Task.objects.filter(

            electrician__phone=request.session['phone']

        ).order_by('-id')

        electrician = Electrician.objects.filter(
            phone=request.session['phone']
        ).first()

        assigned_requests = ClientRequest.objects.filter(
            electrician=electrician.name
        ).exclude(
            status="Completed"
        ).order_by('-id') if electrician else ClientRequest.objects.none()
        attach_request_workflow(assigned_requests)

    else:

        tasks_list = Task.objects.none()
        assigned_requests = ClientRequest.objects.none()

    # ================= SEARCH =================

    search = request.GET.get('search')

    if search:

        tasks_list = tasks_list.filter(

            name__icontains=search

        )

    # ================= STATUS FILTER =================

    status = request.GET.get('status')

    if status:

        tasks_list = tasks_list.filter(

            status=status

        )

    # ================= ADD / UPDATE =================

    if request.method == 'POST':

        action = request.POST.get('action')

        # ================= ADD TASK =================

        if action == "add":

            # ADMIN ONLY

            if not is_admin(request):

                return redirect('/tasks/')

            Task.objects.create(

                name=request.POST.get('name'),

                electrician_id=request.POST.get(
                    'electrician'
                ),

                job_id=request.POST.get(
                    'job'
                ),

                status=request.POST.get(
                    'status'
                ) or "Pending"

            )

        # ================= ADMIN UPDATE =================

        elif action == "update":

            if not is_admin(request):

                return redirect('/tasks/')

            task = Task.objects.get(

                id=request.POST.get('id')

            )

            task.electrician_id = request.POST.get(
                'electrician'
            )

            task.job_id = request.POST.get(
                'job'
            )

            task.status = request.POST.get(
                'status'
            ) or "Pending"

            task.save()
            sync_job_completion(task.job)

        # ================= ELECTRICIAN STATUS UPDATE =================

        elif action == "status_update":

            task = Task.objects.get(

                id=request.POST.get('id')

            )

            # SECURITY CHECK

            if task.electrician.phone != request.session['phone']:

                return redirect('/tasks/')

            task.status = request.POST.get(
                'status'
            ) or "Pending"

            task.save()
            sync_job_completion(task.job)

        return redirect('/tasks/')

    return render(request, 'tasks.html', {

        'tasks': tasks_list,

        'electricians': Electrician.objects.all(),

        'jobs': Job.objects.all(),

        'assigned_requests': assigned_requests

    })


# ================= DELETE TASK =================

def delete_task(request, id):

    if check_login(request):

        return check_login(request)

    # ADMIN ONLY

    if not is_admin(request):

        return redirect('/dashboard/')

    Task.objects.filter(

        id=id

    ).delete()

    return redirect('/tasks/')

# ================= MATERIALS =================

def materials(request):

    if check_login(request):

        return check_login(request)

    # ================= ROLE BASED ACCESS =================

    if is_admin(request):

        materials_list = Material.objects.all().order_by('-id')

    elif is_electrician(request):

        return redirect('/tasks/')

    else:

        return redirect('/client-dashboard/')

    # ================= SEARCH =================

    search = request.GET.get('search')

    if search:

        materials_list = materials_list.filter(

            name__icontains=search

        )

    # ================= ADD / UPDATE =================

    if request.method == 'POST':

        # ONLY ADMIN CAN MANAGE

        if not is_admin(request):

            return redirect('/materials/')

        action = request.POST.get('action')

        # ================= ADD =================

        if action == "add":

            Material.objects.create(

                name=request.POST.get('name'),

                quantity=request.POST.get(
                    'quantity'
                ),

                cost=request.POST.get(
                    'cost'
                ),
                
                job_id=request.POST.get('job'),

            )

        # ================= UPDATE =================

        elif action == "update":

            material = Material.objects.get(

                id=request.POST.get('id')

            )

            material.name = request.POST.get(
                'name'
            )

            material.quantity = request.POST.get(
                'quantity'
            )

            material.cost = request.POST.get(
                'cost'
            )
            material.job_id = request.POST.get('job')
            material.save()

        return redirect('/materials/')

    return render(request, 'materials.html', {
        'materials': materials_list,
        'jobs': Job.objects.all()
 })


# ================= DELETE MATERIAL =================

def delete_material(request, id):

    if check_login(request):

        return check_login(request)

    # ADMIN ONLY

    if not is_admin(request):

        return redirect('/materials/')

    Material.objects.filter(

        id=id

    ).delete()

    return redirect('/materials/')


# ================= REPORTS =================

def reports(request):

    if check_login(request):

        return check_login(request)

    # ADMIN ONLY

    if not is_admin(request):

        return redirect('/dashboard/')

    # ================= JOB REPORTS =================

    completed_jobs = Job.objects.filter(
        status="Completed"
    ).count()

    pending_jobs = Job.objects.filter(
        status="Pending"
    ).count()

    inprogress_jobs = Job.objects.filter(
        status="In Progress"
    ).count()

    # ================= TASK REPORTS =================

    completed_tasks = Task.objects.filter(
        status="Completed"
    ).count()

    pending_tasks = Task.objects.filter(
        status="Pending"
    ).count()

    inprogress_tasks = Task.objects.filter(
        status="In Progress"
    ).count()

    # ================= ELECTRICIANS =================

    electricians = Electrician.objects.all()
    top_electricians = Electrician.objects.all().order_by(
        '-rating',
        '-total_reviews',
        'name'
    )[:5]

    # ================= TOTAL TASKS =================

    total_tasks = (

        completed_tasks +

        pending_tasks +

        inprogress_tasks

    )

    # ================= TOTAL JOBS =================

    total_jobs = (

        completed_jobs +

        pending_jobs +

        inprogress_jobs

    )

    return render(request, 'reports.html', {

        'completed_jobs': completed_jobs,

        'pending_jobs': pending_jobs,

        'inprogress_jobs': inprogress_jobs,

        'completed_tasks': completed_tasks,

        'pending_tasks': pending_tasks,

        'inprogress_tasks': inprogress_tasks,

        'electricians': electricians,

        'top_electricians': top_electricians,

        'total_tasks': total_tasks,

        'total_jobs': total_jobs,

        'total_payments': Payment.objects.filter(
            status='Paid'
        ).count(),

        'total_revenue': sum(
            payment.amount
            for payment in Payment.objects.filter(
                status='Paid'
            )
        ),

        'successful_payments': Payment.objects.filter(
            status='Paid'
        ).count()

    })

# ================= PROFILE =================
def profile(request):
    if check_login(request):

        return check_login(request)

    user = User.objects.get(

        id=request.session['user_id']

    )

    if request.method == "POST":

        if user.role != "Client":

            image = request.FILES.get(
                'profile_image'
            )

            if image:

                user.profile_image = image

            user.save()

            if user.role == "Electrician":

                electrician = Electrician.objects.filter(
                    phone=user.phone
                ).first()

                if electrician:

                    electrician.availability = request.POST.get(
                        'availability'
                    )

                    electrician.save()

            return redirect('/profile/')

    electrician = None

    if user.role == "Electrician":

        electrician = Electrician.objects.filter(
            phone=user.phone
        ).first()

    return render(

        request,

        'profile.html',

        {

            'user': user,

            'electrician': electrician

        }

    )


# ================= UPLOAD REPORT =================

def upload_report(request):

    if check_login(request):

        return check_login(request)

    # ONLY ADMIN & ELECTRICIAN

    if not (

        is_admin(request)

        or

        is_electrician(request)

    ):

        return redirect('/dashboard/')

    if request.method == 'POST':

        form = ReportForm(

            request.POST,

            request.FILES

        )

        if form.is_valid():

            form.save()

            return redirect('/reports/')

    else:

        form = ReportForm()

    return render(request, 'upload_report.html', {

        'form': form

    })

# ================= API TASKS =================

def api_tasks(request):

    # LOGIN CHECK

    if check_login(request):

        return JsonResponse({

            'error': 'Login Required'

        })

    tasks = Task.objects.all().values(

        'id',

        'name',

        'status'

    )

    return JsonResponse(

        list(tasks),

        safe=False

    )


# ================= API ADD TASK =================

def api_add_task(request):

    # LOGIN CHECK

    if check_login(request):

        return JsonResponse({

            'error': 'Login Required'

        })

    # ADMIN ONLY

    if not is_admin(request):

        return JsonResponse({

            'error': 'Access Denied'

        })

    if request.method == "POST":

        data = json.loads(request.body)

        task = Task.objects.create(

            name=data.get('name'),

            electrician_id=data.get(
                'electrician'
            ),

            job_id=data.get('job'),

            status=data.get(
                'status',
                'Pending'
            )

        )

        return JsonResponse({

            'message': 'Task Added',

            'task_id': task.id

        })

    return JsonResponse({

        'error': 'Invalid Request'

    })


# ================= API UPDATE TASK =================

def api_update_task(request, id):

    # LOGIN CHECK

    if check_login(request):

        return JsonResponse({

            'error': 'Login Required'

        })

    # ADMIN ONLY

    if not is_admin(request):

        return JsonResponse({

            'error': 'Access Denied'

        })

    try:

        task = Task.objects.get(id=id)

    except Task.DoesNotExist:

        return JsonResponse({

            'error': 'Task Not Found'

        })

    if request.method == "PUT":

        data = json.loads(request.body)

        task.name = data.get(

            'name',

            task.name

        )

        task.status = data.get(

            'status',

            task.status

        )

        task.save()

        return JsonResponse({

            'message': 'Task Updated'

        })

    return JsonResponse({

        'error': 'Invalid Request'

    })


# ================= API DELETE TASK =================

def api_delete_task(request, id):

    # LOGIN CHECK

    if check_login(request):

        return JsonResponse({

            'error': 'Login Required'

        })

    # ADMIN ONLY

    if not is_admin(request):

        return JsonResponse({

            'error': 'Access Denied'

        })

    try:

        task = Task.objects.get(id=id)

    except Task.DoesNotExist:

        return JsonResponse({

            'error': 'Task Not Found'

        })

    if request.method == "DELETE":

        task.delete()

        return JsonResponse({

            'message': 'Task Deleted'

        })

    return JsonResponse({

        'error': 'Invalid Request'

    })

# ================= CLIENT REQUESTS ADMIN =================

def client_requests(request):

    if check_login(request):

        return check_login(request)

    # ADMIN ONLY

    if not is_admin(request):

        return redirect('/dashboard/')

    requests_data = ClientRequest.objects.all().order_by('-id')

    # ================= UPDATE REQUEST =================

    if request.method == 'POST':

        request_id = request.POST.get('id')

        client_request = ClientRequest.objects.get(
            id=request_id
        )
        client_request.electrician = request.POST.get(
            'electrician'
        )

        client_request.quoted_amount = request.POST.get(
            'quoted_amount'
        ) or 0

        client_request.advance_amount = request.POST.get(
            'advance_amount'
        ) or 0

        client_request.is_quote_approved = (
            request.POST.get(
                'is_quote_approved'
            ) == 'on'
        )

        if request.POST.get('electrician') != "Not Assigned":

            electrician_user = User.objects.filter(

                phone=Electrician.objects.get(

                    name=request.POST.get(
                        'electrician'
                    )

                ).phone

            ).first()

            if electrician_user:

                Notification.objects.create(
                    user=electrician_user,
                    notification_type="Request",
                    title="New Service Request",
                    message=f"New service assigned for {client_request.service_title}"
                )

        client_request.save()

        return redirect('/client-requests/')

    attach_request_workflow(requests_data)

    for item in requests_data:
        request_pincode = item.pincode or pincode_from_text(item.location)
        item.suggested_electricians = [
            electrician
            for electrician in Electrician.objects.all()
            if request_pincode
            and electrician.service_area_pincode == request_pincode
        ]

    return render(request, 'client_requests.html', {

        'requests_data': requests_data,

        'electricians': Electrician.objects.all()

    })


# ================= PAYMENTS =================

def payments(request):

    if check_login(request):

        return check_login(request)

    if is_electrician(request):

        return redirect('/tasks/')

    current_user = User.objects.get(

        id=request.session['user_id']

    )

    # ================= CREATE PAYMENT =================

    if request.method == 'POST':

        import razorpay

        client = razorpay.Client(auth=(

            settings.RAZORPAY_KEY_ID,

            settings.RAZORPAY_KEY_SECRET

        ))

        amount = Decimal(request.POST.get('amount'))

        payment_type = request.POST.get(
            'payment_type'
        )
        # ================= RECEIVER =================

        # CLIENT -> ADMIN

        if is_client(request):

            receiver_id = request.POST.get(
                'receiver'
            )

            receiver = User.objects.get(
                id=receiver_id
            )

        # ADMIN -> ELECTRICIAN

        else:

            receiver_phone = request.POST.get(
                'receiver'
            )

            receiver_electrician = Electrician.objects.get(
                phone=receiver_phone
            )

            receiver = User.objects.get(
                phone=receiver_electrician.phone
            )

        # ================= CREATE ORDER =================

        razorpay_order = client.order.create({

            "amount": int(amount * 100),

            "currency": "INR",

            "payment_capture": "1"

        })

        # ================= SAVE PAYMENT =================

        payment = Payment.objects.create(

            payer=current_user,

            receiver=receiver,

            amount=amount,

            payment_type=payment_type,

            payment_method="Razorpay",

            status='Pending'

        )

        return render(request, 'payment_checkout.html', {

            'payment': payment,

            'razorpay_order_id': razorpay_order['id'],

            'razorpay_key': settings.RAZORPAY_KEY_ID,

            'amount': int(amount * 100)

        })

    # ================= ROLE BASED PAYMENTS =================

    if is_admin(request):

        payments = Payment.objects.all().order_by('-id')

    elif is_electrician(request):

        payments = Payment.objects.filter(

            receiver=current_user

        ).order_by('-id')

    else:

        payments = Payment.objects.filter(

            payer=current_user

        ).order_by('-id')

    # ================= DROPDOWNS =================

    admin = User.objects.filter(
        role='Admin'
    ).first()

    electricians = Electrician.objects.all()

    paid_total = sum(
        payment.amount
        for payment in payments
        if payment.status == "Paid"
    )
    pending_total = sum(
        payment.amount
        for payment in payments
        if payment.status == "Pending"
    )

    return render(request, 'payments.html', {

        'admin': admin,

        'electricians': electricians,

        'payments': payments,

        'paid_total': paid_total,

        'pending_total': pending_total

    })


# ================= PAYMENT SUCCESS =================

def payment_success(request):

    if check_login(request):

        return check_login(request)

    if request.method == "POST":

        import razorpay

        payment_id = request.POST.get(
            'payment_id'
        )

        razorpay_payment_id = request.POST.get(
            'razorpay_payment_id'
        )

        razorpay_order_id = request.POST.get(
            'razorpay_order_id'
        )

        razorpay_signature = request.POST.get(
            'razorpay_signature'
        )

        try:

            payment = Payment.objects.get(
                id=payment_id
            )

            # ================= RAZORPAY CLIENT =================

            client = razorpay.Client(auth=(

                settings.RAZORPAY_KEY_ID,

                settings.RAZORPAY_KEY_SECRET

            ))

            # ================= VERIFY SIGNATURE =================

            params_dict = {

                'razorpay_order_id':
                    razorpay_order_id,

                'razorpay_payment_id':
                    razorpay_payment_id,

                'razorpay_signature':
                    razorpay_signature

            }

            client.utility.verify_payment_signature(
                params_dict
            )

            # ================= UPDATE PAYMENT =================

            payment.status = "Paid"

            payment.transaction_id = (
                razorpay_payment_id
            )

            payment.save()
            Notification.objects.create(
                user=payment.receiver,
                notification_type="Payment",
                title="Payment Received",
                message=f"Payment of ₹{payment.amount} received."
            )

            return JsonResponse({

                'status': 'success'

            })

        except Exception as e:

            payment.status = "Failed"


            payment.save()

            return JsonResponse({

                'status': 'failed',

                'error': str(e)

            })

    return JsonResponse({

        'status': 'invalid request'

    })
# ================= FAQ =================

def faq(request):

    if check_login(request):

        return check_login(request)

    faqs = FAQ.objects.all().order_by('-id')

    if request.method == "POST":

        if is_admin(request):

            FAQ.objects.create(

                question=request.POST.get(
                    'question'
                ),

                answer=request.POST.get(
                    'answer'
                )

            )

            return redirect('/faq/')

    return render(

        request,

        'faq.html',

        {

            'faqs': faqs

        }

    )


# ================= NOTIFICATIONS =================

def notifications(request):

    if check_login(request):

        return check_login(request)

    notifications = Notification.objects.filter(

        user_id=request.session['user_id']

    ).order_by('-id')

    return render(

        request,

        'notifications.html',

        {

            'notifications': notifications

        }

    )


# ================= REVIEWS =================

def reviews(request):

    if check_login(request):
        return check_login(request)

    if request.method == "POST":

        if not is_client(request):

            return redirect('/reviews/')

        electrician_id = request.POST.get(
            'electrician'
        )

        rating = request.POST.get(
            'rating'
        )

        review_text = request.POST.get(
            'review'
        )

        client = User.objects.get(
            id=request.session['user_id']
        )

        Review.objects.update_or_create(

            electrician_id=electrician_id,

            client=client,

            defaults={

                'rating': rating,

                'review': review_text

            }

        )

        electrician = Electrician.objects.get(
            id=electrician_id
        )

        reviews_list = Review.objects.filter(
            electrician=electrician
        )

        electrician.total_reviews = (
            reviews_list.count()
        )

        electrician.rating = round(

            sum(
                r.rating
                for r in reviews_list
            ) / reviews_list.count(),

            1

        )

        electrician.save()

        Notification.objects.create(

            user=User.objects.filter(
                phone=electrician.phone
            ).first(),

            notification_type='Review',

            title='New Review',

            message='A client submitted a review.'

        )

        return redirect('/reviews/')

    if is_electrician(request):

        electrician = Electrician.objects.filter(
            phone=request.session['phone']
        ).first()

        reviews_data = Review.objects.filter(
            electrician=electrician
        ).order_by('-id')

    else:

        reviews_data = Review.objects.all().order_by('-id')

    total_reviews = reviews_data.count()
    average_rating = round(
        sum(review.rating for review in reviews_data) / total_reviews,
        1
    ) if total_reviews else 0

    return render(

        request,

        'reviews.html',

        {

            'reviews': reviews_data,

            'electricians':
            Electrician.objects.all(),

            'total_reviews': total_reviews,

            'average_rating': average_rating

        }

    )


def mark_notification_read(request, id):

    if check_login(request):
        return check_login(request)

    notification = Notification.objects.filter(
        id=id,
        user_id=request.session['user_id']
    ).first()

    if notification:
        notification.is_read = True
        notification.save()

    return redirect('/notifications/')
def generate_service_otp(request, id):

    if check_login(request):
        return check_login(request)

    if not is_electrician(request):
        return redirect('/tasks/')

    client_request = ClientRequest.objects.get(
        id=id
    )

    electrician = Electrician.objects.get(
        phone=request.session['phone']
    )

    if client_request.electrician != electrician.name:
        return JsonResponse({
            'error': 'Access Denied'
        })

    otp = str(
        random.randint(
            100000,
            999999
        )
    )

    ServiceOTP.objects.create(
        client_request=client_request,
        generated_by=electrician,
        otp=otp
    )

    return JsonResponse({
        'otp': otp
    })
def verify_service_otp(request, id):

    if check_login(request):
        return check_login(request)

    if request.method == "POST":

        otp = request.POST.get('otp')

        otp_record = ServiceOTP.objects.filter(
            client_request_id=id,
            otp=otp,
            is_verified=False
        ).first()

        if otp_record:

            if (
                is_client(request)
                and
                otp_record.client_request.client_id != request.session['user_id']
            ):
                return JsonResponse({
                    'status': 'failed'
                })

            otp_record.is_verified = True
            otp_record.save()

            client_request = otp_record.client_request

            client_request.status = "In Progress"
            client_request.save()

            return JsonResponse({
                'status': 'success'
            })

    return JsonResponse({
        'status': 'failed'
    })
