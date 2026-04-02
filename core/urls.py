from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import complaint_detail, login_view,register_view,logout_view,submit_feedback,profile,faqs,reset_password,maintenance_request,update_status
from .views import student_dashboard,staff_dashboard, admin_dashboard,file_complaint,resolve_complaint,assign_staff,my_complaints,assigned_complaints,edit_profile
from .views import assign_complaint
from .views import home
urlpatterns = [
    path("", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("home/", home, name="home"),
    
    path("student/", student_dashboard, name="student"),
    path("staff/", staff_dashboard, name="staff"),
    path("admin_dashboard/", admin_dashboard, name="admin_dashboard"),
    
    path("logout/", logout_view, name="logout"),
    
    path('file_complaint/',file_complaint, name='file_complaint'),
    path("my-complaints/", my_complaints, name="my_complaints"),
    path('update-status/<int:id>/', update_status, name="update_status"),
    path('complaint-detail/<int:grievance_id>/', complaint_detail, name="complaint_detail"),


    path('profile/', profile, name='profile'),
    path('faqs/', faqs, name='faqs'),
    path('reset-password/', reset_password, name='reset_password'),
    path('maintenance-request/', maintenance_request, name='maintenance_request'),
    path("assign/<int:grievance_id>/", assign_complaint, name="assign_complaint"),
    path("feedback/<int:grievance_id>/", submit_feedback, name="submit_feedback"),
        
    path("assign_staff/<int:authority_id>/", assign_staff, name="assign_staff"),
    
    path("resolve/<int:id>/",resolve_complaint, name="resolve_complaint"),
    path("assigned/", assigned_complaints, name="assigned_complaints"),
    path("edit-profile/", edit_profile, name="edit_profile")
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
