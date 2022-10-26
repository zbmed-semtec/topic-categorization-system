from django.urls import path

from . import views

urlpatterns = [
    # ex: /query/
    path('', views.index, name='index'),
    # ex: /query/results/5/
    path('results/<int:meshlist_id>/', views.results, name='results'),
]