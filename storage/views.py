from random import choice

from django.shortcuts import render, redirect
from .forms import RegisterForm
from .models import User, Warehouse, Storage, UserStorage
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.contrib.auth import logout, login, authenticate


def index(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            phonenumber = form.cleaned_data['phonenumber']
            email = form.cleaned_data['email']
            password = make_password(form.cleaned_data['password'])

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('account')
            else:
                data = User(phonenumber=phonenumber, email=email, password=password)
                data.save()
                return redirect('account')
    
    sample_warehouse = choice(
        Warehouse.objects.with_annotations()
    )
    context = {
        'form': form,
        'warehouse': sample_warehouse,
        'user_authorised': request.user.is_authenticated
    }
    return render(request, 'index.html', context)


def get_boxes(request):
    warehouses = Warehouse.objects.with_annotations()
    for warehouse in warehouses:
        warehouse.storages_list = list(warehouse.storages.all())
        warehouse.storages_lt_three = list(
            warehouse.storages.with_area().filter(area__lt=3)
        )
        warehouse.storages_lt_ten = list(
            warehouse.storages.with_area().filter(area__lt=10)
        )
        warehouse.storages_gt_ten = list(
            warehouse.storages.with_area().filter(area__gte=10)
        )
    
    context = {
        'warehouses': warehouses,
        'user_authorised': request.user.is_authenticated
    }
    return render(request, 'boxes.html', context)


def get_faq(request):
    context = {'user_authorised': request.user.is_authenticated}
    return render(request, 'faq.html', context)


def get_confidential(request):
    context = {'user_authorised': request.user.is_authenticated}
    return render(request, 'confidential.html', context)


def logout_user(request):
    logout(request)
    return redirect('index')


def login_user(request):
    if request.method == 'POST':

        email = request.POST.get('EMAIL')
        password = request.POST.get('PASSWORD')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('account')
    context = {'user_authorised': request.user.is_authenticated}
    return render(request, 'login.html', context)


def register_user(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            phonenumber = form.cleaned_data['phonenumber']
            email = form.cleaned_data['email']
            password = make_password(form.cleaned_data['password'])
            data = User(phonenumber=phonenumber, email=email, password=password)
            data.save()
            return redirect('login')
    context = {
        'form': form,
    }
    return render(request, 'registration.html', context)


@login_required(login_url='index')
def get_account(request):
    user = request.user
    user_storages = UserStorage.objects.filter(user=user).annotate(address=F('warehouse__address'))
    context = {
        'user': request.user,
        'storages': user_storages,
        'user_authorised': request.user.is_authenticated
    }
    return render(request, 'my-rent.html', context)


@login_required(login_url='index')
def make_order(request, warehouse_id, storage_id):
    print(warehouse_id, storage_id)
    return redirect('index')
