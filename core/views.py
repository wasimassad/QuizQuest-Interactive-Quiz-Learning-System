from django.shortcuts import render
from datetime import datetime

def home(request):
    context = {"year": datetime.now().year}
    return render(request, "home.html", context)
