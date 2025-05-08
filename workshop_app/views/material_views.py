"""
Material views module.

This file now imports all views from the material_views package.
It maintains backward compatibility with code that imports from here.
"""

# Re-export all views from the material_views package
from workshop_app.views.material_views import (
    material_list,
    material_detail,
    add_material, 
    edit_material,
    withdraw_material,
    return_material,
    get_material_qr_code,
    material_history,
    delete_material_attachment,
    get_active_job,
    clear_active_job,
    start_timer
)

# Keep all the exported names in __all__
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
