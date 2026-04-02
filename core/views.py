from multiprocessing import context
from re import search
from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import (
    Grievance,
    GrievanceCategory,
    Authority,
    GrievanceStatusHistory,
    GrievanceAttachment,
    Feedback,
    Profile
)

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request,username=email, password=password)

        if user is not None:
            login(request, user)
            
            authority=Authority.objects.filter(user=user).first()
            if not authority:
                return render(request,"login.html",{"error":"No Profile found"})
            role=authority.role

            if role == "student":
                return redirect("student")

            elif role == "staff":
                return redirect("staff")

            elif role == "admin":
                return redirect("admin_dashboard")
        else:
            return render(request,"login.html",{"error":"Invalid credentials"})

    return render(request, "login.html")


def register_view(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role = request.POST.get("role")
        if password != confirm_password:
            return render(request, "register.html", {"error": "Passwords do not match"})
        if User.objects.filter(username=email).exists():
            return render(request, "register.html", {"error": "User already exists"})
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=fullname
        )
        Authority.objects.create(user=user, role=role)
        
        return redirect("login")

    return render(request, "register.html")


def home(request):
    
    total = Grievance.objects.count()
    resolved = Grievance.objects.filter(status="Resolved").count()
    pending = Grievance.objects.exclude(status="Resolved").count()

    context = {
        'total': total,
        'resolved': resolved,
        'pending': pending
    }

    return render(request, "home.html", context)

from django.db.models import Count
@login_required

def student_dashboard(request):

    grievances = Grievance.objects.filter(student=request.user)

    total = grievances.count()

    pending = grievances.filter(status="Pending").count()
    review = grievances.filter(status="In Progress").count()
    resolved = grievances.filter(status="Resolved").count()

    if total == 0:
        pending_percent = review_percent = resolved_percent = 0
    else:
        pending_percent = (pending / total) * 100
        review_percent = (review / total) * 100
        resolved_percent = (resolved / total) * 100

    context = {
        "grievances": grievances,
        "pending_percent": pending_percent,
        "review_percent": review_percent,
        "resolved_percent": resolved_percent,
    }

    return render(request, "student.html", context)


@login_required
def staff_dashboard(request):

    authority = Authority.objects.filter(user=request.user).first()
    if not authority:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')

    grievances = Grievance.objects.filter(authority=authority)

    total = grievances.count()
    resolved = grievances.filter(status="Resolved").count()
    pending = grievances.exclude(status="Resolved").count()

    return render(request,"staff.html",{
        "grievances":grievances,
        "total":total,
        "resolved":resolved,
        "pending":pending
    })
@login_required
def admin_dashboard(request):
    authority = Authority.objects.filter(user=request.user).first()
    if not authority or authority.role != "admin":
        return redirect('login')
    total = Grievance.objects.count()
    resolved = Grievance.objects.filter(status="Resolved").count()
    pending = Grievance.objects.exclude(status="Resolved").count()

    categories = GrievanceCategory.objects.count()
    authorities = Authority.objects.count()
    recent = Grievance.objects.order_by("-created_at")[:5]
    grievances = Grievance.objects.all()

    context = {
        "total": total,
        "resolved": resolved,
        "pending": pending,
        "categories": categories,
        "authorities": authorities,
        "recent": recent,
        "grievances": grievances,   
    }
    search = request.GET.get("search")
    status = request.GET.get("status")
    date = request.GET.get("date")
    grievances = Grievance.objects.all()
    
    if search:
      grievances = grievances.filter(title__icontains=search)

    if status:
      grievances = grievances.filter(status=status)
    if date:
        grievances = grievances.filter(created_at__date=date)
          
    return render(request, "admin_dashboard.html", context)

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def file_complaint(request):
    categories = GrievanceCategory.objects.all()
    if request.method == "POST":
        print("FORM HIT")
        
        title = request.POST.get("title")
        description = request.POST.get("description")
        category_name = request.POST.get("category")

        category = GrievanceCategory.objects.get(category_name=category_name)
        authority = Authority.objects.filter(category=category).first()
        grievance=Grievance.objects.create(
            student=request.user,
            title=title,
            description=description,
            category=category,
            authority=authority
        )
        
        messages.success(request, "Complaint filed successfully!")
        return redirect("student")
    return render(request, "file_complaint.html", {"categories": categories})


def resolve_complaint(request, id):
    complaint = Grievance.objects.get(id=id)
    complaint.status = "Resolved"
    complaint.save()
    return redirect("staff")

def assign_staff(request, id):
    
    complaint = Grievance.objects.get(id=id)

    staff = User.objects.filter(profile__role="staff")

    if request.method == "POST":

        staff_id = request.POST.get("staff")

        complaint.assigned_staff_id = staff_id
        complaint.status = "Assigned"
        complaint.save()

        return redirect("admin")

    return render(request, "assign_staff.html",
                  {"complaint": complaint, "staff": staff})
    
@login_required
def my_complaints(request):
    grievances = Grievance.objects.filter(student=request.user).order_by("-created_at")
    return render(request, "my_complaints.html", {"grievances": grievances})

@login_required
def submit_feedback(request, grievance_id):
    grievance = get_object_or_404(
        Grievance,
        id=grievance_id,
        student=request.user
    )
    if grievance.status != "Resolved":
        return redirect("complaint_detail", grievance_id=grievance.id)

    if request.method == "POST":

        rating = request.POST.get("rating")
        comments = request.POST.get("comments")

        feedback, created = Feedback.objects.get_or_create(
            grievance=grievance
       )

        feedback.rating = rating
        feedback.comments = comments
        feedback.save()

        return redirect("my_complaints")

    return render(request, "submit_feedback.html", {
        "grievance": grievance
    })
    
@login_required
def profile(request):
    authority = Authority.objects.filter(user=request.user).first()
    if not authority:
        return render(request, "profile.html", {
            "user": request.user,
            "error": "No profile found"
        })

    # 🔥 Role-based template selection
    if authority.role == "staff":
        return render(request, "staff_profile.html", {
            "user": request.user,
            "authority": authority
        })

    elif authority.role == "student":
        return render(request, "student_profile.html", {
            "user": request.user,
            "authority": authority
        })
    elif authority.role == "admin":
        return render(request, "admin_profile.html", {
            "user": request.user,
            "authority": authority
    })

    return render(request, "profile.html", {
        "user": request.user,
        "authority": authority
    })

def faqs(request):
    return render(request, "faqs.html")

def reset_password(request):
    return render(request, "reset_password.html")

def maintenance_request(request):
    return render(request, "maintenance_request.html")

@login_required
def update_status(request,id):

    grievance = Grievance.objects.get(id=id)

    if request.method == "POST":

        new_status = request.POST.get("status")
        remarks = request.POST.get("remarks")
        grievance.status = new_status
        grievance.save()

        GrievanceStatusHistory.objects.create(
            grievance=grievance,
            status=new_status,
            remarks=remarks,
            updated_by=request.user
        )

        return redirect("staff")

    return render(request,"update_status.html",
                  {"grievance":grievance})

@login_required
def complaint_detail(request, grievance_id):

    grievance = get_object_or_404(
        Grievance,
        id=grievance_id,
        student=request.user
    )

    history = GrievanceStatusHistory.objects.filter(
        grievance=grievance
    ).order_by('-updated_at')

    return render(request, "complaint_detail.html", {
        "grievance": grievance,
        "history": history
    })
def assigned_complaints(request):
    authority = Authority.objects.filter(user=request.user).first()

    grievances = Grievance.objects.filter(authority=authority)

    return render(request, "assigned_complaints.html", {
        "grievances": grievances
    })
def edit_profile(request):
    authority = Authority.objects.filter(user=request.user).first()

    if request.method == "POST":
       
        request.user.email = request.POST.get('email')
        request.user.save()

        # Only for staff
        if authority.role == "staff":
            authority.designation = request.POST.get('designation')
            authority.save()

        return redirect('profile')

    return render(request, 'edit_profile.html', {
        'user': request.user,
        'authority': authority
    })
def assign_complaint(request, grievance_id):
    grievance = Grievance.objects.get(id=grievance_id)
    authorities = Authority.objects.all()

    if request.method == "POST":
        authority_id = request.POST.get("authority")
        authority = Authority.objects.get(id=authority_id)

        grievance.authority = authority
        grievance.save()

        return redirect("admin_dashboard")

    return render(request, "assign_complaint.html", {
        "grievance": grievance,
        "authorities": authorities
    })