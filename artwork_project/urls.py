"""
URL configuration for artwork_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from artwork import views as artwork_view
from imageprocessor import views as imageprocessor_view

urlpatterns = [
    path('admin/', admin.site.urls),
#    path('artworks/add/', artwork_view.add_artwork, name='add_artwork'),
#    path('artworks/', artwork_view.list_artworks, name='list_artworks'),
    path('admin/', admin.site.urls),
    path('upload/', imageprocessor_view.upload_image, name='upload_image'),
    path('images/<str:image_name>', imageprocessor_view.fetch_image, name='fetch_image'),
    path('text_to_speech/', imageprocessor_view.google_text_to_speech, name='text_to_speech'),
    path('ai/', imageprocessor_view.generate_text_using_ai, name='ai'),
    path('csrf/', imageprocessor_view.csrf_token, name='csrf_token'),
]
