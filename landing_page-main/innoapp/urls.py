from django.urls import path

from . import views

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("list/", views.event_list, name="list"),
    path("details/", views.details, name="details"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("save-text/", views.save_text, name="save_text"),
    path("upload-image/", views.upload_image, name="upload_image"),
    path("upload-video/", views.upload_video, name="upload_video"),
    path("update-youtube/", views.update_youtube, name="update_youtube"),
    path("update-social/", views.update_social, name="update_social"),
]
