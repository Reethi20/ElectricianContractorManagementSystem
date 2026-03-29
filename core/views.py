from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime


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
            return redirect('/dashboard/')
        else:
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

    return render(request, 'dashboard.html', {
        'electricians': Electrician.objects.count(),
        'jobs': Job.objects.count(),
        'tasks': Task.objects.filter(status="Pending").count(),
        'completed': Task.objects.filter(status="Completed").count()
    })


# ================= ELECTRICIANS =================
def electricians(request):
    if check_login(request): return check_login(request)

    if request.method == 'POST':
        if request.session.get('role') != "Admin":
            return redirect('/dashboard/')

        action = request.POST.get('action')

        if action == "add":
            Electrician.objects.create(
                name=request.POST['name'],
                phone=request.POST['phone']
            )

        elif action == "update":
            e = Electrician.objects.get(id=request.POST['id'])
            e.name = request.POST['name']
            e.phone = request.POST['phone']
            e.save()

        return redirect('/electricians/')

    return render(request, 'electricians.html', {
        'electricians': Electrician.objects.all()
    })


def delete_electrician(request, id):
    if request.session.get('role') != "Admin":
        return redirect('/dashboard/')
    Electrician.objects.get(id=id).delete()
    return redirect('/electricians/')


# ================= JOBS =================
def jobs(request):
    if check_login(request): return check_login(request)

    if request.method == 'POST':
        if request.session.get('role') != "Admin":
            return redirect('/dashboard/')

        action = request.POST.get('action')

        if action == "add":
            Job.objects.create(
                title=request.POST['title'],
                location=request.POST['location'],
                electrician_id=request.POST['electrician'],
                deadline=request.POST['deadline'],
                status=request.POST['status']
            )

        elif action == "update":
            j = Job.objects.get(id=request.POST['id'])
            j.title = request.POST['title']
            j.location = request.POST['location']
            j.electrician_id = request.POST['electrician']
            j.deadline = datetime.strptime(request.POST['deadline'], "%Y-%m-%d")
            j.status = request.POST['status']
            j.save()

        return redirect('/jobs/')

    return render(request, 'jobs.html', {
        'jobs': Job.objects.all(),
        'electricians': Electrician.objects.all()
    })


def delete_job(request, id):
    if request.session.get('role') != "Admin":
        return redirect('/dashboard/')
    Job.objects.get(id=id).delete()
    return redirect('/jobs/')


# ================= TASKS =================
def tasks(request):
    if check_login(request): return check_login(request)

    if request.method == 'POST':
        if request.session.get('role') != "Admin":
            return redirect('/dashboard/')

        action = request.POST.get('action')

        if action == "add":
            Task.objects.create(
                name=request.POST['name'],
                electrician_id=request.POST['electrician'],
                status=request.POST['status']
            )

        elif action == "update":
            t = Task.objects.get(id=request.POST['id'])
            t.name = request.POST['name']
            t.electrician_id = request.POST['electrician']
            t.status = request.POST['status']
            t.save()

        return redirect('/tasks/')

    return render(request, 'tasks.html', {
        'tasks': Task.objects.all(),
        'electricians': Electrician.objects.all()
    })


def delete_task(request, id):
    if request.session.get('role') != "Admin":
        return redirect('/dashboard/')
    Task.objects.get(id=id).delete()
    return redirect('/tasks/')


# ================= MATERIALS =================
def materials(request):
    if check_login(request): return check_login(request)

    if request.method == 'POST':
        if request.session.get('role') != "Admin":
            return redirect('/dashboard/')

        action = request.POST.get('action')

        if action == "add":
            Material.objects.create(
                name=request.POST['name'],
                quantity=request.POST['quantity']
            )

        elif action == "update":
            m = Material.objects.get(id=request.POST['id'])
            m.name = request.POST['name']
            m.quantity = request.POST['quantity']
            m.save()

        return redirect('/materials/')

    return render(request, 'materials.html', {
        'materials': Material.objects.all()
    })


def delete_material(request, id):
    if request.session.get('role') != "Admin":
        return redirect('/dashboard/')
    Material.objects.get(id=id).delete()
    return redirect('/materials/')


# ================= REPORTS =================
def reports(request):
    if check_login(request): return check_login(request)

    return render(request, 'reports.html', {
        'jobs': Job.objects.count(),
        'tasks': Task.objects.count(),
        'electricians': Electrician.objects.count()
    })


# ================= PROFILE =================
def profile(request):
    if check_login(request): return check_login(request)

    user = User.objects.get(id=request.session['user_id'])
    return render(request, 'profile.html', {'user': user})