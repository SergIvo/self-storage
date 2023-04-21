from django.shortcuts import render
from .forms import RegisterForm


def index(request):
    form = RegisterForm()

    if request.method == 'Post':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
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
