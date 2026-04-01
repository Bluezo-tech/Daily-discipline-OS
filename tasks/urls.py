from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.task_list, name="task_list"),
    path("today/", views.today_tasks, name="today_tasks"),
    path("upcoming/", views.upcoming_tasks, name="upcoming_tasks"),

    path("create/", views.task_create, name="task_create"),
    path("<int:pk>/update/", views.task_update, name="task_update"),
    path("<int:pk>/delete/", views.task_delete, name="task_delete"),
    path("<int:pk>/toggle/", views.task_toggle, name="task_toggle"),

    path("check-reminders/", views.check_reminders, name="check_reminders"),
]