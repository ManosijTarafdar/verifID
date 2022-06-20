from django import views
from django.contrib import admin
from django.urls import path , include
from . import views

urlpatterns = [
    path('',views.home,name='studentHome'),
    path('myAnnouncements/',views.announcements,name='announcementHome'),
    path('viewAnnouncement/<str:id>/',views.view_announcement,name='viewAnnouncement'),
    path('myAssignments/',views.assignments,name='assignmentsHome'),
]