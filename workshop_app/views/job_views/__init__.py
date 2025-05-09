"""
Job views package.
Import and re-export all views from submodules for backward compatibility.
"""

from workshop_app.views.job_views.list_views import job_list
from workshop_app.views.job_views.detail_views import job_detail, get_job_qr_code
from workshop_app.views.job_views.edit_views import add_job, edit_job
from workshop_app.views.job_views.api_views import get_client_contacts

# Re-export all views
__all__ = [
    'job_list',
    'job_detail',
    'add_job',
    'edit_job',
    'get_client_contacts',
    'get_job_qr_code',
]
