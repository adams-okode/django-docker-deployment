from django.shortcuts import render, redirect

# Create your views here.


def default(request):
    return redirect('home-page')

def home_page(request):
    return render(request,'web_home/index.html', {})

