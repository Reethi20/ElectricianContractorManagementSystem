from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from datetime import date
import re
import random
import json
from .models import *
from .forms import JobForm, ReportForm
import razorpay
from django.conf import settings

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

# ================= HOME =================
def home(request):
    return render(request, 'index.html')

# ================= REGISTER =================
def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        role = request.POST.get('role')
        password = request.POST.get('password')

        # EMPTY FIELD CHECK
        if not all([name, phone, email, role, password]):
            return render(request, 'register.html', {
                'error': 'All fields are required'
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


# ================= DASHBOARD =================
def dashboard(request):
    if check_login(request):
        return check_login(request)
    # ADMIN ONLY
    if not is_admin(request):
        return redirect('/tasks/')
    tasks = Task.objects.all().order_by('-id')[:5]
    payments = Payment.objects.all().order_by('-id')[:5]
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
        'payments': payments
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

    # CREATE REQUEST
    if request.method == 'POST':
        ClientRequest.objects.create(
            client=client,
            service_title=request.POST.get(
                'service_title'
            ),
            location=request.POST.get(
                'location'
            ),
            description=request.POST.get(
                'description'
            ),
        )
        return redirect('/my-requests/')
    requests_data = ClientRequest.objects.filter(
        client=client
    ).order_by('-id')
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

                Electrician.objects.create(

                    name=name,

                    phone=phone

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

    elif is_electrician(request):

        tasks_list = Task.objects.filter(

            electrician__phone=request.session['phone']

        ).order_by('-id')

    else:

        tasks_list = Task.objects.none()

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

        return redirect('/tasks/')

    return render(request, 'tasks.html', {

        'tasks': tasks_list,

        'electricians': Electrician.objects.all(),

        'jobs': Job.objects.all()

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

        # ELECTRICIANS CAN VIEW ONLY

        materials_list = Material.objects.all().order_by('-id')

    else:

        # CLIENTS NO ACCESS

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
                )

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

            material.save()

        return redirect('/materials/')

    return render(request, 'materials.html', {

        'materials': materials_list

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

        'total_tasks': total_tasks,

        'total_jobs': total_jobs,

        'total_payments': Payment.objects.count(),

        'successful_payments': Payment.objects.filter(
            status='Success'
        ).count()

    })

# ================= PROFILE =================


def profile(request):

    if check_login(request):

        return check_login(request)

    user = User.objects.get(

        id=request.session['user_id']

    )

    return render(request, 'profile.html', {

        'user': user

    })


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

        client_request.status = request.POST.get(
            'status'
        )

        client_request.save()

        return redirect('/client-requests/')

    return render(request, 'client_requests.html', {

        'requests_data': requests_data,

        'electricians': Electrician.objects.all()

    })


# ================= PAYMENTS =================

# ================= PAYMENTS =================

def payments(request):

    if check_login(request):

        return check_login(request)

    current_user = User.objects.get(

        id=request.session['user_id']

    )

    # ================= RAZORPAY CLIENT =================

    client = razorpay.Client(auth=(

        settings.RAZORPAY_KEY_ID,

        settings.RAZORPAY_KEY_SECRET

    ))

    # ================= CREATE PAYMENT =================

    if request.method == 'POST':

        amount = int(request.POST.get('amount'))

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

            "amount": amount * 100,

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

            'amount': amount * 100

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

    return render(request, 'payments.html', {

        'admin': admin,

        'electricians': electricians,

        'payments': payments

    })


# ================= PAYMENT SUCCESS =================

def payment_success(request):

    if check_login(request):

        return check_login(request)

    if request.method == "POST":

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

            payment.status = "Success"

            payment.transaction_id = (
                razorpay_payment_id
            )

            payment.save()

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