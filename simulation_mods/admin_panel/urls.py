from django.urls import path
from . import views
app_name = "admin_panel"
urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('message/<int:message_id>/toggle-status/', views.admin_toggle_message_status, name='admin_toggle_message_status'),
    path('mod/<uuid:mod_id>/toggle-visibility/', views.admin_toggle_visibility, name='admin_toggle_visibility'),
    path('mod/<uuid:mod_id>/delete/', views.admin_delete_mod, name='admin_delete_mod'),
    path('mod/<uuid:mod_id>/edit/', views.admin_mod_edit, name='admin_mod_edit'),
    path('mod/<uuid:mod_id>/view/', views.admin_mod_view, name='admin_mod_view'),
    path('user/<int:user_id>/edit/', views.admin_mod_user_edit, name='admin_mod_user_edit'),
    path('user/<int:user_id>/password/', views.admin_mod_user_password, name='admin_mod_user_password'),
    path('user/<int:user_id>/delete/', views.admin_delete_user, name='admin_delete_user'),
]
