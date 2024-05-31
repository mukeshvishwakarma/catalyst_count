from django.urls import path
from main import views
from main.views import ChunkedUploadView

urlpatterns = [
    path('', views.user_login), 
    path('user_login', views.user_login, name="user_login"),
    path('upload/', views.upload_file, name='upload'),
    path('upload-chunk/', ChunkedUploadView.as_view(), name='upload_chunk'),
    path('upload_success/', views.upload_success, name='upload_success'),
    path('filter/', views.filter_data, name='filter'),
    path('user/', views.userdata,name='user'),
    path('adduser/', views.adduserdata,name='adduser'),
    
]
