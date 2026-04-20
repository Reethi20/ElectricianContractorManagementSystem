from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import *
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime, date

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
        if not request.POST.get('name') or not request.POST.get('password'):
            return HttpResponse("All fields required")

        User.objects.create(
            name=request.POST['name'],
            phone=request.POST['phone'],
            email=request.POST['email'],
            role=request.POST['role'],
            password=make_password(request.POST['password'])
        )
        return redirect('/login/')
    return render(request, 'register.html')


# ================= LOGIN =================
def login_view(request):
    if request.method == 'POST':
        user = User.objects.filter(email=request.POST['email']).first()

        if user and check_password(request.POST['password'], user.password):
            request.session['user_id'] = user.id
            request.session['role'] = user.role
            request.session['name'] = user.name
            return redirect('/dashboard/')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


# ================= LOGOUT =================
def logout(request):
    request.session.flush()
    return redirect('/login/')

def forgot_password(request):
    if request.method == "POST":
        user = User.objects.filter(email=request.POST['email']).first()

        if user:
            user.password = make_password(request.POST['password'])
            user.save()
            return redirect('/login/')
        else:
            return render(request, 'forgot_password.html', {
                'error': 'Email not found'
            })

    return render(request, 'forgot_password.html')
# ================= DASHBOARD =================
def dashboard(request):
    if check_login(request): return check_login(request)

    due_jobs = Job.objects.filter(deadline__lt=date.today(), status="Pending")
    completed_tasks = Task.objects.filter(status="Completed")
    new_tasks = Task.objects.filter(status="Pending").order_by('-id')[:3]

    return render(request, 'dashboard.html', {
        'electricians': Electrician.objects.count(),
        'jobs': Job.objects.count(),
        'tasks': Task.objects.filter(status="Pending").count(),
        'completed': Task.objects.filter(status="Completed").count(),

        'due_jobs': due_jobs,
        'completed_tasks': completed_tasks,
        'new_tasks': new_tasks
    })


# ================= ELECTRICIANS =================
def electricians(request):
    if check_login(request): return check_login(request)

    if not is_admin(request):
        return redirect('/dashboard/')

    search = request.GET.get('search')
    electricians_list = Electrician.objects.filter(name__icontains=search) if search else Electrician.objects.all()

    if request.method == 'POST':
        Electrician.objects.create(
            name=request.POST['name'],
            phone=request.POST['phone']
        )
        return redirect('/electricians/')

    return render(request, 'electricians.html', {'electricians': electricians_list})


def delete_electrician(request, id):
    if not is_admin(request):
        return redirect('/dashboard/')
    try:
        Electrician.objects.get(id=id).delete()
    except Electrician.DoesNotExist:
        pass
    return redirect('/electricians/')


# ================= JOBS =================
def jobs(request):
    if check_login(request): return check_login(request)

    search = request.GET.get('search')
    jobs_list = Job.objects.filter(title__icontains=search) if search else Job.objects.all()

    if request.method == 'POST':
        if not is_admin(request):
            return redirect('/dashboard/')

        if not request.POST.get('title'):
            return HttpResponse("Title required")

        Job.objects.create(
            title=request.POST['title'],
            location=request.POST['location'],
            electrician_id=request.POST['electrician'],
            deadline=request.POST['deadline'],
            status=request.POST['status']
        )
        return redirect('/jobs/')

    return render(request, 'jobs.html', {
        'jobs': jobs_list,
        'electricians': Electrician.objects.all()
    })


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
    if check_login(request): return check_login(request)

    status_filter = request.GET.get('status')

    if is_admin(request):
        task_list = Task.objects.all()
    else:
        task_list = Task.objects.filter(electrician__name=request.session.get('name'))

    if status_filter:
        task_list = task_list.filter(status=status_filter)

    if request.method == 'POST':
        task = Task.objects.get(id=request.POST['id'])

        if is_admin(request):
            task.name = request.POST['name']
            task.electrician_id = request.POST['electrician']
            task.job_id = request.POST['job']
            task.status = request.POST['status']
        else:
            # electrician can update only their task
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
    if check_login(request): return check_login(request)

    if request.method == 'POST':
        if not is_admin(request):
            return redirect('/dashboard/')

        Material.objects.create(
            name=request.POST['name'],
            quantity=request.POST['quantity']
        )
        return redirect('/materials/')

    return render(request, 'materials.html', {
        'materials': Material.objects.all()
    })


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
    if check_login(request): return check_login(request)

    return render(request, 'reports.html', {
        'today_jobs': Job.objects.filter(status="Completed").count(),
        'completed_tasks': Task.objects.filter(status="Completed").count(),
        'pending_tasks': Task.objects.filter(status="Pending").count(),
        'electricians': Electrician.objects.all()
    })

# ================= PROFILE =================
def profile(request):
    if check_login(request): return check_login(request)

    user = User.objects.get(id=request.session['user_id'])
    return render(request, 'profile.html', {'user': user})

# ================= API =================
def api_tasks(request):
    if not request.session.get('user_id'):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

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

    return JsonResponse({'tasks': data}, status=200)


def api_add_task(request):
    if request.method == "POST":
        if not is_admin(request):
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        task = Task.objects.create(
            name=request.POST['name'],
            electrician_id=request.POST['electrician'],
            job_id=request.POST['job'],
            status=request.POST['status']
        )

        return JsonResponse({'message': 'Task added', 'id': task.id}, status=201)


def api_update_task(request, id):
    try:
        task = Task.objects.get(id=id)
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)

    if request.method == "POST":

        if is_admin(request):
            task.name = request.POST.get('name', task.name)
            task.status = request.POST.get('status', task.status)

        elif is_electrician(request):
            if task.electrician.name != request.session.get('name'):
                return JsonResponse({'error': 'Unauthorized'}, status=403)

            task.status = request.POST.get('status', task.status)

        task.save()
        return JsonResponse({'message': 'Task updated'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def api_delete_task(request, id):
    if not is_admin(request):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        Task.objects.get(id=id).delete()
        return JsonResponse({'message': 'Deleted successfully'}, status=200)
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)