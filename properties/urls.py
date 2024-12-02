from django.urls import path
from .views import (Properties,Addproperty,Propertydetail,Editproperty,Deleteproperty,DeleteNotificationView,NotificationsPageView)

urlpatterns=[
    path("properties/",Properties.as_view(),name='properties'),
    path("add_property/",Addproperty.as_view(),name='add_property'),
    path("property_detail/<str:property_id>/",Propertydetail.as_view(),name='property_detail'),
    path("edit_property/<str:property_id>/",Editproperty.as_view(),name='edit_property'),
    path("delete_property/<str:property_id>/",Deleteproperty.as_view(),name='delete_property'),
    path('notifications/', NotificationsPageView.as_view(), name='notifications'),
    path('notification/delete/', DeleteNotificationView.as_view(), name='delete_notification'),
    
]