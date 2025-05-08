from django.contrib import admin
from workshop_app.models import (
    MaterialCategory, MaterialType, Material,
    MachineType, Machine, JobStatus, Job,
    Client, ContactPerson, Operator, StaffSettings,
    AttachmentType, MaterialAttachment
)

# Material admin
admin.site.register(MaterialCategory)
admin.site.register(MaterialType)
admin.site.register(Material)
admin.site.register(AttachmentType)
admin.site.register(MaterialAttachment)

# Machine admin
admin.site.register(MachineType)
admin.site.register(Machine)

# Job admin
admin.site.register(JobStatus)
admin.site.register(Job)

# Client admin
admin.site.register(Client)
admin.site.register(ContactPerson)

# User admin
admin.site.register(Operator)
admin.site.register(StaffSettings)
