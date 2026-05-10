from django.urls import path

from .views import library_musik, upload_musik, delete_musik

urlpatterns = [
    path('', upload_musik, name='upload_musik'),
    path('library/', library_musik, name='library_musik'),
    path('delete/<uuid:musik_id>/', delete_musik, name='delete_musik'),
]
