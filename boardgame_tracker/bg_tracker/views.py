from django.shortcuts import render
from django.views.generic import ListView, View, CreateView, DetailView


class HomePage(View):

    def get(self, request):
        return render(request, 'bg_tracker/index.html')
