# workshop_app/admin.py

from django.contrib import admin
from workshop_app.models import (
    MaterialCategory, MaterialType, Material,
    MachineType, Machine, JobStatus, Job,
    Client, ContactPerson, Operator, StaffSettings,
    AttachmentType, MaterialAttachment, MaterialTransaction
)

# Material admin
admin.site.register(MaterialCategory)
admin.site.register(MaterialType)
admin.site.register(Material)
admin.site.register(AttachmentType)
admin.site.register(MaterialAttachment)

# Simple Material Transaction admin
class MaterialTransactionAdmin(admin.ModelAdmin):
    list_display = ['material', 'transaction_type', 'quantity', 'transaction_date', 'job_reference', 'operator_name']
    list_filter = ['transaction_type', 'transaction_date']
    search_fields = ['material__name', 'material__material_id', 'job_reference', 'operator_name']

# Register the Material Transaction model with the admin
admin.site.register(MaterialTransaction, MaterialTransactionAdmin)

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
