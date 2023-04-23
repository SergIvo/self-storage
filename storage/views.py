from random import choice

from django.shortcuts import render, redirect
from .forms import RegisterForm
from .models import User, Warehouse, Storage, UserStorage
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Min


def index(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            phonenumber = form.cleaned_data['phonenumber']
            email = form.cleaned_data['email']
            password = make_password(form.cleaned_data['password'])
            data = User(phonenumber=phonenumber, email=email, password=password)
            data.save()
            return redirect('account')
    
    sample_warehouse = choice(
        Warehouse.objects.annotate(
            free_storages=F('total_storages') - Count('storages_in_use'),
            min_price=Min('storages__price')
        )
    )
    context = {
        'form': form,
        'warehouse': sample_warehouse
    }
    return render(request, 'index.html', context)


def get_boxes(request):
    warehouses = Warehouse.objects.prefetch_related('storages').annotate(
        free_storages=F('total_storages') - Count('storages_in_use'), 
        min_price=Min('storages__price')
    )
    for warehouse in warehouses:
        warehouse.storages_list = list(warehouse.storages.all())
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            phonenumber = form.cleaned_data['phonenumber']
            email = form.cleaned_data['email']
            password = make_password(form.cleaned_data['password'])
            data = User(phonenumber=phonenumber, email=email, password=password)
            data.save()
            return redirect('account')
    
    context = {'warehouses': warehouses}
    return render(request, 'boxes.html', context)


def get_faq(request):
    context = {}
    return render(request, 'faq.html', context)


def get_confidential(request):
    context = {}
    return render(request, 'confidential.html', context)


@login_required
def get_account(request):
    user = request.user
    user_storages = UserStorage.objects.filter(user=user).annotate(address=F('warehouse__address'))
    context = {
        'user': request.user,
        'storages': user_storages}
    return render(request, 'my-rent.html', context)
