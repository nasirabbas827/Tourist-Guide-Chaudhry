from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/update/", views.profile_update, name="profile_update"),
    path("destinations/", views.destination_list, name="destination_list"),
    path("tips/", views.tips_list, name="tips_list"),
    path("plans/", views.travelplan_list, name="travelplan_list"),
    path("plans/create/", views.travelplan_create, name="travelplan_create"),
    path("plans/<int:pk>/update/", views.travelplan_update, name="travelplan_update"),
    path("plans/<int:pk>/delete/", views.travelplan_delete, name="travelplan_delete"),
    path("destinations/<int:pk>/", views.destination_detail, name="destination_detail"),
    path("gallery/", views.gallery, name="gallery"),
    path("services/", views.service_list, name="service_list"),
    path("services/create/", views.service_create, name="service_create"),
    path("services/<int:pk>/update/", views.service_update, name="service_update"),
    path("services/<int:pk>/delete/", views.service_delete, name="service_delete"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)