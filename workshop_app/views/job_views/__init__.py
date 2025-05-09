"""
Job views package.
Import and re-export all views from submodules for backward compatibility.
"""

from workshop_app.views.job_views.list_views import job_list
from workshop_app.views.job_views.detail_views import job_detail, job_detail_by_pk, get_job_qr_code
from workshop_app.views.job_views.edit_views import add_job, edit_job, edit_job_by_pk, activate_job_by_pk
from workshop_app.views.job_views.api_views import get_client_contacts

# Re-export all views
__all__ = [
    'job_list',
    'job_detail',
    'job_detail_by_pk',
    'add_job',
    'edit_job',
    'edit_job_by_pk',
    'get_client_contacts',
    'get_job_qr_code',
    'activate_job_by_pk',
]
