from django.db import models
from django.contrib.auth.models import User

# -----------------------------
# Profile (Role Management)
# -----------------------------

class Profile(models.Model):
    
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('authority', 'Authority'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    roll_number = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


# -----------------------------
# Complaint Categories
# -----------------------------

class GrievanceCategory(models.Model):
    
    category_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.category_name

class Authority(models.Model):
    
    designation = models.CharField(max_length=100)
    ROLE_CHOICES=[
        ('student','Student'),
        ('staff','Staff'),
        ('admin','Admin'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role=models.CharField(max_length=15,choices=ROLE_CHOICES)
    category = models.ForeignKey(
        GrievanceCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    def __str__(self):
        if self.category:
          return f"{self.designation}-{self.category.category_name}"
        return self.designation

        
# -----------------------------
# Grievance / Complaint
# -----------------------------

class Grievance(models.Model):
    
    STATUS_CHOICES = (
        ('Pending','Pending'),
        ('Assigned','Assigned'),
        ('In Progress','In Progress'),
        ('Resolved','Resolved'),
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="student_grievances"
    )

    category = models.ForeignKey(
        GrievanceCategory,
        on_delete=models.SET_NULL,
        null=True
    )

    authority = models.ForeignKey(
        Authority,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# -----------------------------
# Grievance Attachments
# -----------------------------
class GrievanceAttachment(models.Model):
    
    grievance = models.ForeignKey(
        Grievance,
        on_delete=models.CASCADE
    )

    file = models.FileField(upload_to="attachments/")

# -----------------------------
# Grievance status history
# -----------------------------

class GrievanceStatusHistory(models.Model):
    
    grievance = models.ForeignKey(
        Grievance,
        on_delete=models.CASCADE
    )

    status = models.CharField(max_length=20)

    remarks = models.TextField(blank=True)

    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    updated_at = models.DateTimeField(auto_now_add=True)


class Feedback(models.Model):
    
    grievance = models.OneToOneField(
        Grievance,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField()

    comments = models.TextField(blank=True)
