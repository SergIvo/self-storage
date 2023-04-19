from django.shortcuts import render

# Create your views here.


def index(request):
    context = {}
    return render(request, 'index.html', context)


def get_boxes(request):
    context = {}
    return render(request, 'boxes.html', context)
