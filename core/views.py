from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from datetime import date
import re

from .models import *
from .forms import JobForm, ReportForm


# ================= ROLE CHECK =================

def is_admin(request):

    return request.session.get('role') == "Admin"


def is_electrician(request):

    return request.session.get('role') == "Electrician"


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

        # PASSWORD LENGTH

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

            # ROLE REDIRECT

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

    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.filter(email=email).first()

        if not user:

            return render(request, 'forgot_password.html', {
                'error': 'Email not found'
            })

        if len(password) < 8:

            return render(request, 'forgot_password.html', {
                'error': 'Password must be at least 8 characters'
            })

        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).+$'

        if not re.match(pattern, password):

            return render(request, 'forgot_password.html', {
                'error': 'Password must contain uppercase, lowercase, number and special character'
            })

        user.password = make_password(password)
        user.save()

        return redirect('/login/')

    return render(request, 'forgot_password.html')


# ================= DASHBOARD =================

def dashboard(request):

    if check_login(request):

        return check_login(request)

    tasks = Task.objects.all().order_by('-id')[:5]

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

        'tasks': tasks

    })

# ================= CLIENT DASHBOARD =================

def client_dashboard(request):

    if check_login(request):

        return check_login(request)

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
        ).count()

    })


# ================= MY REQUESTS =================

def my_requests(request):

    if check_login(request):

        return check_login(request)

    # CURRENT CLIENT

    client = User.objects.get(

        id=request.session['user_id']

    )

    # CREATE REQUEST

    if request.method == 'POST':

        ClientRequest.objects.create(

            client=client,

            service_title=request.POST['service_title'],

            location=request.POST['location'],

            description=request.POST['description']

        )

        return redirect('/my-requests/')

    # ONLY CLIENT REQUESTS

    requests_data = ClientRequest.objects.filter(

        client=client

    )

    return render(request, 'my_requests.html', {

        'requests_data': requests_data,

        'total_requests': requests_data.count(),

        'completed_requests': requests_data.filter(
            status='Completed'
        ).count(),

        'pending_requests': requests_data.filter(
            status='Pending'
        ).count()

    })


# ================= ELECTRICIANS =================

def electricians(request):

    if check_login(request):

        return check_login(request)

    electricians_list = Electrician.objects.all()

    search = request.GET.get('search')

    if search:

        electricians_list = electricians_list.filter(
            name__icontains=search
        )

    # ================= ADD / UPDATE =================

    if request.method == 'POST':

        if not is_admin(request):

            return redirect('/dashboard/')

        action = request.POST.get('action')

        # ================= ADD =================

        if action == "add":

            name = request.POST.get('name')

            phone = request.POST.get('phone')

            # PREVENT DUPLICATE PHONE

            if not Electrician.objects.filter(
                phone=phone
            ).exists():

                Electrician.objects.create(

                    name=name,
                    phone=phone

                )

        # ================= UPDATE =================

        elif action == "update":

            electrician = Electrician.objects.get(
                id=request.POST.get('id')
            )

            electrician.name = request.POST.get('name')

            electrician.phone = request.POST.get('phone')

            electrician.save()

        return redirect('/electricians/')

    return render(request, 'electricians.html', {

        'electricians': electricians_list

    })


# ================= REGISTER =================

def register(request):

    if request.method == 'POST':

        name = request.POST.get('name')

        phone = request.POST.get('phone')

        email = request.POST.get('email')

        role = request.POST.get('role')

        password = request.POST.get('password')

        # EMPTY CHECK

        if not all([name, phone, email, role, password]):

            return render(request, 'register.html', {

                'error': 'All fields are required'

            })

        # PASSWORD LENGTH

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

        # EMAIL EXISTS

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

        # AUTO LINK ELECTRICIAN

        if role == "Electrician":

            electrician = Electrician.objects.filter(
                phone=phone
            ).first()

            # CREATE IF NOT EXISTS

            if not electrician:

                Electrician.objects.create(

                    name=name,
                    phone=phone

                )

        return redirect('/login/')

    return render(request, 'register.html')

# ================= DELETE ELECTRICIAN =================

def delete_electrician(request, id):

    if not is_admin(request):

        return redirect('/dashboard/')

    Electrician.objects.filter(id=id).delete()

    return redirect('/electricians/')


# ================= JOBS =================

# ================= JOBS =================

def jobs(request):

    if check_login(request):

        return check_login(request)

    # ================= ADMIN =================

    if request.session['role'] == "Admin":

        jobs_list = Job.objects.all()

    # ================= ELECTRICIAN =================

    elif request.session['role'] == "Electrician":

        jobs_list = Job.objects.filter(

            electrician__phone=request.session['phone']

        )

    # ================= OTHER USERS =================

    else:

        jobs_list = Job.objects.none()

    # SEARCH

    search = request.GET.get('search')

    if search:

        jobs_list = jobs_list.filter(
            title__icontains=search
        )

    # ================= ADMIN CRUD =================

    if request.method == 'POST':

        if not is_admin(request):

            return redirect('/jobs/')

        action = request.POST.get('action')

        # ADD

        if action == "add":

            Job.objects.create(

                title=request.POST['title'],

                location=request.POST['location'],

                electrician_id=request.POST['electrician'],

                deadline=request.POST['deadline'],

                status=request.POST['status'],

                image=request.FILES.get('image')

            )

        # UPDATE

        elif action == "update":

            job = Job.objects.get(
                id=request.POST['id']
            )

            job.title = request.POST['title']

            job.location = request.POST['location']

            job.electrician_id = request.POST['electrician']

            job.deadline = request.POST['deadline']

            job.status = request.POST['status']

            if request.FILES.get('image'):

                job.image = request.FILES.get('image')

            job.save()

        return redirect('/jobs/')

    return render(request, 'jobs.html', {

        'jobs': jobs_list,

        'electricians': Electrician.objects.all()

    })


# ================= DELETE JOB =================

def delete_job(request, id):

    if not is_admin(request):

        return redirect('/dashboard/')

    Job.objects.filter(id=id).delete()

    return redirect('/jobs/')

# ================= TASKS =================

# ================= TASKS =================

# ================= TASKS =================

def tasks(request):

    # LOGIN CHECK

    if check_login(request):

        return check_login(request)

    # ================= ADMIN =================

    if request.session['role'] == "Admin":

        tasks_list = Task.objects.all().order_by('-id')

    # ================= ELECTRICIAN =================

    elif request.session['role'] == "Electrician":

        tasks_list = Task.objects.filter(

            electrician__phone=request.session['phone']

        ).order_by('-id')

    # ================= OTHER USERS =================

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

    # ================= POST ACTIONS =================

    if request.method == 'POST':

        action = request.POST.get('action')

        # ================= ADD TASK =================

        if action == "add":

            if not is_admin(request):

                return redirect('/tasks/')

            Task.objects.create(

                name=request.POST.get('name'),

                electrician_id=request.POST.get('electrician'),

                job_id=request.POST.get('job'),

                status=request.POST.get('status')

            )

        # ================= ADMIN UPDATE =================

        elif action == "update":

            if not is_admin(request):

                return redirect('/tasks/')

            task = Task.objects.get(

                id=request.POST.get('id')

            )

            task.name = request.POST.get('name')

            task.electrician_id = request.POST.get('electrician')

            task.job_id = request.POST.get('job')

            task.status = request.POST.get('status')

            task.save()

        # ================= ELECTRICIAN STATUS UPDATE =================

        elif action == "status_update":

            task = Task.objects.get(

                id=request.POST.get('id')

            )

            # SECURITY CHECK

            if task.electrician.phone != request.session['phone']:

                return redirect('/tasks/')

            task.status = request.POST.get('status')

            task.save()

        return redirect('/tasks/')

    # ================= RENDER =================

    return render(request, 'tasks.html', {

        'tasks': tasks_list,

        'electricians': Electrician.objects.all(),

        'jobs': Job.objects.all()

    })


# ================= DELETE TASK =================

def delete_task(request, id):

    if not is_admin(request):

        return redirect('/dashboard/')

    Task.objects.filter(id=id).delete()

    return redirect('/tasks/')


# ================= MATERIALS =================

def materials(request):

    # LOGIN CHECK

    if check_login(request):

        return check_login(request)

    # ================= ADMIN =================

    if request.session['role'] == "Admin":

        materials_list = Material.objects.all().order_by('-id')

    # ================= ELECTRICIAN =================

    elif request.session['role'] == "Electrician":

        # VIEW ONLY

        materials_list = Material.objects.all().order_by('-id')

    # ================= CLIENT / OTHER =================

    else:

        materials_list = Material.objects.none()

    # ================= SEARCH =================

    search = request.GET.get('search')

    if search:

        materials_list = materials_list.filter(

            name__icontains=search

        )

    # ================= ADMIN CRUD =================

    if request.method == 'POST':

        # ONLY ADMIN CAN MODIFY

        if not is_admin(request):

            return redirect('/materials/')

        action = request.POST.get('action')

        # ================= ADD =================

        if action == "add":

            Material.objects.create(

                name=request.POST.get('name'),

                quantity=request.POST.get('quantity')

            )

        # ================= UPDATE =================

        elif action == "update":

            material = Material.objects.get(

                id=request.POST.get('id')

            )

            material.name = request.POST.get('name')

            material.quantity = request.POST.get('quantity')

            material.save()

        return redirect('/materials/')

    # ================= RENDER =================

    return render(request, 'materials.html', {

        'materials': materials_list

    })


# ================= DELETE MATERIAL =================

def delete_material(request, id):

    # ONLY ADMIN

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

    today_jobs = Job.objects.filter(
        status="Completed"
    ).count()

    completed_tasks = Task.objects.filter(
        status="Completed"
    ).count()

    pending_tasks = Task.objects.filter(
        status="Pending"
    ).count()

    inprogress_tasks = Task.objects.filter(
        status="In Progress"
    ).count()

    electricians = Electrician.objects.all()
    return render(request, 'reports.html', {
        'today_jobs': today_jobs,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'inprogress_tasks': inprogress_tasks,
        'electricians': electricians
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


# ================= API TASKS =================

def api_tasks(request):

    tasks = Task.objects.all()

    data = []

    for t in tasks:

        data.append({
            'id': t.id,
            'name': t.name,
            'electrician': t.electrician.name,
            'job': t.job.title,
            'status': t.status
        })

    return JsonResponse({
        'tasks': data
    })


# ================= API ADD TASK =================

def api_add_task(request):

    if not is_admin(request):

        return JsonResponse({
            'error': 'Unauthorized'
        }, status=403)

    if request.method == 'POST':

        task = Task.objects.create(
            name=request.POST['name'],
            electrician_id=request.POST['electrician'],
            job_id=request.POST['job'],
            status=request.POST['status']
        )

        return JsonResponse({
            'message': 'Task added',
            'id': task.id
        })

    return JsonResponse({
        'error': 'Invalid request'
    })


# ================= API UPDATE TASK =================

def api_update_task(request, id):

    try:

        task = Task.objects.get(id=id)

    except Task.DoesNotExist:

        return JsonResponse({
            'error': 'Task not found'
        }, status=404)

    if request.method == 'POST':

        task.status = request.POST.get(
            'status',
            task.status
        )

        task.save()

        return JsonResponse({
            'message': 'Task updated'
        })

    return JsonResponse({
        'error': 'Invalid request'
    })


# ================= API DELETE TASK =================

def api_delete_task(request, id):

    if not is_admin(request):

        return JsonResponse({
            'error': 'Unauthorized'
        }, status=403)

    Task.objects.filter(id=id).delete()

    return JsonResponse({
        'message': 'Deleted successfully'
    })


# ================= UPLOAD REPORT =================

def upload_report(request):

    if check_login(request):

        return check_login(request)

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
# ================= CLIENT REQUESTS ADMIN =================

def client_requests(request):

    if check_login(request):

        return check_login(request)

    # ONLY ADMIN

    if request.session['role'] != "Admin":

        return redirect('/dashboard/')

    requests_data = ClientRequest.objects.all().order_by('-id')

    # ================= UPDATE =================

    if request.method == 'POST':

        request_id = request.POST.get('id')

        client_request = ClientRequest.objects.get(id=request_id)

        client_request.electrician = request.POST.get('electrician')

        client_request.status = request.POST.get('status')

        client_request.payment_status = request.POST.get('payment_status')

        client_request.save()

        return redirect('/client-requests/')

    return render(request, 'client_requests.html', {

        'requests_data': requests_data,

        'electricians': Electrician.objects.all()

    })