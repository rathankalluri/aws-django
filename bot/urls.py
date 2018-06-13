from django.contrib import admin
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
	path('instances/', views.instances, name='instances'),
	path('instances/<filter>/', views.instances, name='instances'),
	path('instances/<filter>/<mode>', views.instances, name='instances'),
	path('create_instance/', views.create_instance, name='create_instance'),
	path('delete_instance/', views.delete_instance, name='delete_instance'),
	path('ec2_op/<op>/<ecid>/',views.ec2_op, name='ec2_op'),
	path('ec2_op/<op>/<ecid>/<mode>/',views.ec2_op, name='ec2_op'),
]
