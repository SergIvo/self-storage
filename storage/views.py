from random import choice

from django.shortcuts import render, redirect
from .forms import RegisterForm
from .models import User, Warehouse, Storage, UserStorage, storages_with_address
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.contrib.auth import logout, login, authenticate
from django.utils import timezone


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
        warehouse_storages = list(
            Storage.objects.with_characteristics().filter(
                warehouse=warehouse,
                rented_storage=None
            )
        )
        warehouse.free_storages = len(warehouse_storages)
        storages_types = list(
            {storage.storage_type for storage in warehouse_storages}
        )

        warehouse.all_storages = []
        for storage_type in storages_types:
            filtered = [
                storage for storage in warehouse_storages if storage.storage_type == storage_type
            ]
            warehouse.all_storages.append(filtered[0])

        warehouse.storages_lt_three = [
            storage for storage in warehouse.all_storages if storage.area < 3
        ]
        warehouse.storages_lt_ten = [
            storage for storage in warehouse.all_storages if storage.area < 10
        ]
        warehouse.storages_gt_ten = [
            storage for storage in warehouse.all_storages if storage.area >= 10
        ]
    
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
    user_storages = storages_with_address(user.storages)
    context = {
        'user': request.user,
        'storages': user_storages,
        'user_authorised': request.user.is_authenticated
    }
    return render(request, 'my-rent.html', context)


@login_required(login_url='index')
def make_order(request, storage_id):
    storage = Storage.objects.get(id=storage_id)
    start_datetime = rent_start=timezone.now()
    end_datetime = start_datetime.replace(month=start_datetime.month+1)
    rented_storage = UserStorage.objects.create(
        user=request.user,
        storage=storage,
        rent_start=start_datetime,
        rent_end=end_datetime
    )
    return redirect('payment:create_checkout_session', rented_storage.id)
