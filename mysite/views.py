from django.shortcuts import render

def home(requst):
    context = {}
    return render(requst, 'home.html', context)