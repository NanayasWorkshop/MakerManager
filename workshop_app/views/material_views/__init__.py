"""
Material views package.
Import and re-export all views from submodules for backward compatibility.
"""

from workshop_app.views.material_views.list_views import material_list
from workshop_app.views.material_views.detail_views import material_detail, material_history, get_material_qr_code
from workshop_app.views.material_views.edit_views import add_material, edit_material, delete_material_attachment
from workshop_app.views.material_views.transaction_views import withdraw_material, return_material
from workshop_app.views.material_views.api_views import get_active_job, clear_active_job, start_timer

# Re-export all views
__all__ = [
    'material_list',
    'material_detail',
    'add_material',
    'edit_material',
    'withdraw_material',
    'return_material',
    'get_material_qr_code',
    'material_history',
    'delete_material_attachment',
    'get_active_job',
    'clear_active_job',
    'start_timer',
]
