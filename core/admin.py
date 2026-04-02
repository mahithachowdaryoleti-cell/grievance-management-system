# from django.contrib import admin
# from .models import User, Grievance, Response


# admin.site.register(Grievance)
# admin.site.register(Response)


from django.contrib import admin
from .models import *


admin.site.register(Profile)
admin.site.register(GrievanceCategory)
admin.site.register(Authority)
admin.site.register(Grievance)
admin.site.register(GrievanceStatusHistory)
admin.site.register(GrievanceAttachment)
admin.site.register(Feedback)

