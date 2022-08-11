from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('wiki/<str:title>/', views.wiki_page, name='wiki_page'),
    path('wiki/<str:title>/<str:edit>', views.wiki_page, name='edit_page'),
    path('search/', views.search, name='search'),
    path('404/', views.error, name='error'),
    path('newpage/', views.new_page, name='new_page'),
    path('random/', views.random_page, name='random_page')
]
