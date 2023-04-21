from django.shortcuts import render, redirect
from .forms import RegisterForm
from .models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required


def index(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # form.save()
            phonenumber = form.cleaned_data['phonenumber']
            email = form.cleaned_data['email']
            password = make_password(form.cleaned_data['password'])
            data = User(phonenumber=phonenumber, email=email, password=password)
            data.save()
            return redirect('account')
    context = {'form': form}
    return render(request, 'index.html', context)


def get_boxes(request):
    context = {}
    return render(request, 'boxes.html', context)


def get_faq(request):
    context = {}
    return render(request, 'faq.html', context)


def get_confidential(request):
    context = {}
    return render(request, 'confidential.html', context)


@login_required
def get_account(request):
    context = {}
    return render(request, 'my-rent.html', context)
