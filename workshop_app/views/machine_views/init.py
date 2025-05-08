"""
Machine views package.
Import and re-export all views from submodules for backward compatibility.
"""

from workshop_app.views.machine_views.list_views import machine_list
from workshop_app.views.machine_views.detail_views import machine_detail, machine_usage_history, get_machine_qr_code
from workshop_app.views.machine_views.edit_views import add_machine, edit_machine
from workshop_app.views.machine_views.usage_views import start_machine_usage, stop_machine_usage

# Re-export all views
__all__ = [
    'machine_list',
    'machine_detail',
    'machine_usage_history',
    'get_machine_qr_code',
    'add_machine',
    'edit_machine',
    'start_machine_usage',
    'stop_machine_usage',
]
