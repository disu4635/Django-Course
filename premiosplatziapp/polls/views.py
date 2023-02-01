from django.shortcuts import render
from django.http import HttpResponse

def index(req):
    return HttpResponse('Hola Mundo')

# Create your views here.
