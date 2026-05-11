from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import *
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime, date
import re
from .forms import JobForm, ReportForm

# ================= ROLE CHECK =================
def is_admin(request):
    return request.session.get('role') == "Admin"


def is_electrician(request):
    return request.session.get('role') == "Electrician"


# ================= AUTH CHECK =================
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
        password = request.POST.get('password')

        if not name or not password:
            return render(request, 'register.html', {
                'error': 'All fields are required'
            })

        if len(password) < 8:
            return render(request, 'register.html', {
                'error': 'Password must be at least 8 characters'
            })

        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).+$'

        if not re.match(pattern, password):
            return render(request, 'register.html', {
                'error': 'Password must include uppercase, lowercase, number and special character'
            })

        User.objects.create(
            name=name,
            phone=request.POST['phone'],
            email=request.POST['email'],
            role=request.POST['role'],
            password=make_password(password)
        )

        return redirect('/login/')

    return render(request, 'register.html')


# ================= LOGIN =================
def login_view(request):

    if request.method == 'POST':

        user = User.objects.filter(
            email=request.POST['email']
        ).first()

        if user and check_password(
            request.POST['password'],
            user.password
        ):

            request.session['user_id'] = user.id
            request.session['role'] = user.role
            request.session['name'] = user.name

            if user.role == "Admin":
                return redirect('/dashboard/')

            elif user.role == "Electrician":
                return redirect('/tasks/')

            elif user.role == "Client":
                return redirect('/client-dashboard/')

            else:
                return redirect('/')

        else:
            return render(request, 'login.html', {
                'error': 'Invalid credentials'
            })

    return render(request, 'login.html')


# ================= LOGOUT =================
def logout(request):
    request.session.flush()
    return redirect('/login/')


# ================= FORGOT PASSWORD =================
def forgot_password(request):

    if request.method == "POST":

        password = request.POST.get('password')

        if len(password) < 8:
            return render(request, 'forgot_password.html', {
                'error': 'Password must be at least 8 characters'
            })

        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).+$'

        if not re.match(pattern, password):
            return render(request, 'forgot_password.html', {
                'error': 'Password must include uppercase, lowercase, number and special character'
            })

        user = User.objects.filter(
            email=request.POST['email']
        ).first()

        if user:
            user.password = make_password(password)
            user.save()
            return redirect('/login/')

        else:
            return render(request, 'forgot_password.html', {
                'error': 'Email not found'
            })

    return render(request, 'forgot_password.html')


# ================= ADMIN DASHBOARD =================
def dashboard(request):

    if check_login(request):
        return check_login(request)

    due_jobs = Job.objects.filter(
        deadline__lt=date.today(),
        status="Pending"
    )

    completed_tasks = Task.objects.filter(
        status="Completed"
    )

    new_tasks = Task.objects.filter(
        status="Pending"
    ).order_by('-id')[:3]

    return render(request, 'dashboard.html', {
        'electricians': Electrician.objects.count(),
        'jobs': Job.objects.count(),
        'tasks': Task.objects.filter(status="Pending").count(),
        'completed': Task.objects.filter(status="Completed").count(),
        'due_jobs': due_jobs,
        'completed_tasks': completed_tasks,
        'new_tasks': new_tasks
    })


# ================= CLIENT DASHBOARD =================
def client_dashboard(request):

    if check_login(request):
        return check_login(request)

    total_requests = ClientRequest.objects.count()

    completed_requests = ClientRequest.objects.filter(
        status='Completed'
    ).count()

    pending_requests = ClientRequest.objects.filter(
        status='Pending'
    ).count()

    return render(request, 'client_dashboard.html', {
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'pending_requests': pending_requests,
    })


# ================= MY REQUESTS =================
def my_requests(request):

    if check_login(request):
        return check_login(request)

    if request.method == 'POST':

        ClientRequest.objects.create(
            service_title=request.POST['service_title'],
            location=request.POST['location'],
            description=request.POST['description']
        )

        return redirect('/my-requests/')

    requests_data = ClientRequest.objects.all()

    total_requests = requests_data.count()

    completed_requests = requests_data.filter(
        status='Completed'
    ).count()

    pending_requests = requests_data.filter(
        status='Pending'
    ).count()

    return render(request, 'my_requests.html', {
        'requests': requests_data,
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'pending_requests': pending_requests,
    })


# ================= ELECTRICIANS =================
def electricians(request):

    if check_login(request):
        return check_login(request)

    if not is_admin(request):
        return redirect('/dashboard/')

    search = request.GET.get('search')

    if search:
        electricians_list = Electrician.objects.filter(
            name__icontains=search
        )
    else:
        electricians_list = Electrician.objects.all()

    if request.method == 'POST':

        action = request.POST.get('action')

        if action == "add":

            Electrician.objects.create(
                name=request.POST['name'],
                phone=request.POST['phone']
            )

        elif action == "update":

            e = Electrician.objects.get(
                id=request.POST['id']
            )

            e.name = request.POST['name']
            e.phone = request.POST['phone']
            e.save()

        return redirect('/electricians/')

    return render(request, 'electricians.html', {
        'electricians': electricians_list
    })


# ================= DELETE ELECTRICIAN =================
def delete_electrician(request, id):

    if not is_admin(request):
        return redirect('/dashboard/')

    try:
        Electrician.objects.get(id=id).delete()
    except Electrician.DoesNotExist:
        pass

    return redirect('/electricians/')


# ================= JOBS =================
from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import date
from .models import Job, Electrician

def jobs(request):
    if check_login(request):
        return check_login(request)

    # 🔐 Check login
    if not request.session.get('user_id'):
        return redirect('/login/')

    jobs_list = Job.objects.all()
    electricians = Electrician.objects.all()

    # 🔍 Optional search
    search = request.GET.get('search')
    if search:
        jobs_list = jobs_list.filter(title__icontains=search)

    # ================= POST =================
    if request.method == 'POST':
        if not is_admin(request):
        # Only admin allowed
        
            return redirect('/dashboard/')

        action = request.POST.get('action')

        if action == "add":

            Job.objects.create(
                title=request.POST.get('title'),
                location=request.POST['location'],
                image=request.FILES.get('image'),
                electrician_id=request.POST['electrician'],
                deadline=request.POST['deadline'],
                status=request.POST['status']
            )

        elif action == "update":

            j = Job.objects.get(id=request.POST['id'])

            j.title = request.POST['title']
            j.location = request.POST['location']
            j.image = request.FILES.get('image') or j.image
            j.electrician_id = request.POST['electrician']
            j.deadline = request.POST['deadline']
            j.status = request.POST['status']
            j.save()
        # 🔹 Safe data extraction
        title = request.POST.get('title')
        location = request.POST.get('location')
        electrician = request.POST.get('electrician')
        deadline = request.POST.get('deadline')
        status = request.POST.get('status')
        image = request.FILES.get('image')

        # 🔴 Validation (prevents 500 error)
        if not title or not location or not electrician or not deadline or not status:
            return HttpResponse("❌ All fields are required")

        # ================= ADD =================
        if action == "add":
            try:
                Job.objects.create(
                    title=title,
                    location=location,
                    image=image,
                    electrician_id=electrician,
                    deadline=deadline,
                    status=status
                )
            except Exception as e:
                return HttpResponse(f"Error while adding job: {e}")

        # ================= UPDATE =================
        elif action == "update":
            job_id = request.POST.get('id')

            try:
                j = Job.objects.get(id=job_id)
            except Job.DoesNotExist:
                return HttpResponse("❌ Job not found")

            try:
                j.title = title
                j.location = location
                j.electrician_id = electrician
                j.deadline = deadline
                j.status = status

                # keep old image if new not uploaded
                if image:
                    j.image = image

                j.save()

            except Exception as e:
                return HttpResponse(f"Error while updating job: {e}")

        return redirect('/jobs/')

    # ================= GET =================
    return render(request, 'jobs.html', {
        'jobs': jobs_list,
        'electricians': electricians
    })

# ================= DELETE JOB =================
def delete_job(request, id):

    if not is_admin(request):
        return redirect('/dashboard/')

    try:
        Job.objects.get(id=id).delete()
    except Job.DoesNotExist:
        pass

    return redirect('/jobs/')
# ================= TASKS =================
def tasks(request):

    if check_login(request):
        return check_login(request)

    status_filter = request.GET.get('status')

    if is_admin(request):
        task_list = Task.objects.all()
    else:
        task_list = Task.objects.filter(
            electrician__name=request.session.get('name')
        )

    if status_filter:
        task_list = task_list.filter(status=status_filter)

    if request.method == 'POST':

        action = request.POST.get('action')

        if action == "add" and is_admin(request):

            Task.objects.create(
                name=request.POST['name'],
                electrician_id=request.POST['electrician'],
                job_id=request.POST['job'],
                status=request.POST['status']
            )

        elif action == "update":

            try:
                task = Task.objects.get(
                    id=request.POST['id']
                )

            except Task.DoesNotExist:
                return redirect('/tasks/')

            if is_admin(request):

                task.name = request.POST['name']
                task.electrician_id = request.POST['electrician']
                task.job_id = request.POST['job']
                task.status = request.POST['status']

            else:

                if task.electrician.name != request.session.get('name'):
                    return redirect('/tasks/')

                task.status = request.POST['status']

            task.save()

        return redirect('/tasks/')

    return render(request, 'tasks.html', {
        'tasks': task_list,
        'electricians': Electrician.objects.all(),
        'jobs': Job.objects.all()
    })


# ================= DELETE TASK =================
def delete_task(request, id):

    if not is_admin(request):
        return redirect('/dashboard/')

    try:
        Task.objects.get(id=id).delete()
    except Task.DoesNotExist:
        pass

    return redirect('/tasks/')


# ================= MATERIALS =================
def materials(request):

    if check_login(request):
        return check_login(request)

    if request.method == 'POST':

        if not is_admin(request):
            return redirect('/dashboard/')

        action = request.POST.get('action')

        if action == "add":

            Material.objects.create(
                name=request.POST['name'],
                quantity=request.POST['quantity']
            )

        elif action == "update":

            m = Material.objects.get(
                id=request.POST['id']
            )

            m.name = request.POST['name']
            m.quantity = request.POST['quantity']
            m.save()

        return redirect('/materials/')

    return render(request, 'materials.html', {
        'materials': Material.objects.all()
    })


# ================= DELETE MATERIAL =================
def delete_material(request, id):

    if not is_admin(request):
        return redirect('/dashboard/')

    try:
        Material.objects.get(id=id).delete()
    except Material.DoesNotExist:
        pass

    return redirect('/materials/')


# ================= REPORTS =================
def reports(request):

    if check_login(request):
        return check_login(request)

    return render(request, 'reports.html', {
        'today_jobs': Job.objects.filter(status="Completed").count(),
        'completed_tasks': Task.objects.filter(status="Completed").count(),
        'pending_tasks': Task.objects.filter(status="Pending").count(),
        'electricians': Electrician.objects.all()
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

    if not request.session.get('user_id'):
        return JsonResponse({
            'error': 'Unauthorized'
        }, status=401)

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
    }, status=200)


# ================= API ADD TASK =================
def api_add_task(request):

    if request.method == "POST":

        if not is_admin(request):
            return JsonResponse({
                'error': 'Unauthorized'
            }, status=403)

        task = Task.objects.create(
            name=request.POST['name'],
            electrician_id=request.POST['electrician'],
            job_id=request.POST['job'],
            status=request.POST['status']
        )

        return JsonResponse({
            'message': 'Task added',
            'id': task.id
        }, status=201)


# ================= API UPDATE TASK =================
def api_update_task(request, id):

    try:
        task = Task.objects.get(id=id)

    except Task.DoesNotExist:
        return JsonResponse({
            'error': 'Task not found'
        }, status=404)

    if request.method == "POST":

        if is_admin(request):

            task.name = request.POST.get(
                'name',
                task.name
            )

            task.status = request.POST.get(
                'status',
                task.status
            )

        elif is_electrician(request):

            if task.electrician.name != request.session.get('name'):
                return JsonResponse({
                    'error': 'Unauthorized'
                }, status=403)

            task.status = request.POST.get(
                'status',
                task.status
            )

        task.save()

        return JsonResponse({
            'message': 'Task updated'
        }, status=200)

    return JsonResponse({
        'error': 'Invalid request'
    }, status=400)


# ================= API DELETE TASK =================
def api_delete_task(request, id):

    if not is_admin(request):
        return JsonResponse({
            'error': 'Unauthorized'
        }, status=403)

    try:

        Task.objects.get(id=id).delete()

        return JsonResponse({
            'message': 'Deleted successfully'
        }, status=200)

    except Task.DoesNotExist:
        return JsonResponse({
            'error': 'Task not found'
        }, status=404)


# ================= FILE UPLOAD =================
        return JsonResponse({'error': 'Task not found'}, status=404)
    # ================= FILE UPLOAD =================
def upload_job(request):
    return render(request, 'upload_job.html')


def upload_report(request):

    return render(request, 'upload_report.html')

    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_report')
    else:
        form = ReportForm()
    return render(request, 'upload_report.html', {'form': form})

