"""
Views for material listing and filtering.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import connection
from django.conf import settings

from workshop_app.models import Material, MaterialCategory, MaterialType


@login_required
def material_list(request):
    """List materials with search and filter capabilities"""
    # Get filter parameters from request
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    type_id = request.GET.get('type', '')
    stock_filter = request.GET.get('stock', '')
    color_filter = request.GET.get('color', '')  # New color filter parameter
    sort_param = request.GET.get('sort', 'name')
    
    # Start with all materials
    materials = Material.objects.all()
    
    # Apply search filter
    if search_query:
        materials = materials.filter(
            Q(name__icontains=search_query) |
            Q(material_id__icontains=search_query) |
            Q(supplier_name__icontains=search_query) |
            Q(brand_name__icontains=search_query) |
            Q(location_in_workshop__icontains=search_query)
        )
    
    # Apply category filter
    if category_id:
        materials = materials.filter(material_type__category_id=category_id)
    
    # Apply type filter
    if type_id:
        materials = materials.filter(material_type_id=type_id)
    
    # Apply stock filter
    if stock_filter == 'low':
        materials = materials.filter(minimum_stock_alert=True)
    elif stock_filter == 'out':
        materials = materials.filter(current_stock__lte=0)
    elif stock_filter == 'available':
        materials = materials.filter(current_stock__gt=0)
    
    # Apply color filter (new)
    if color_filter:
        materials = materials.filter(color__iexact=color_filter)
    
    # Apply sorting
    if sort_param == 'name':
        materials = materials.order_by('name')
    elif sort_param == 'id':
        materials = materials.order_by('material_id')
    elif sort_param == 'stock':
        materials = materials.order_by('current_stock')
    elif sort_param == 'category':
        materials = materials.order_by('material_type__category__name', 'material_type__name')
    elif sort_param == 'location':
        materials = materials.order_by('location_in_workshop')
    elif sort_param == 'color':  # New sort option
        materials = materials.order_by('color')
    
    # Get categories and types for filter dropdowns
    categories = MaterialCategory.objects.all().order_by('name')
    material_types = MaterialType.objects.all().order_by('name')
    
    # Get unique colors for color filter dropdown (new)
    colors = Material.objects.values_list('color', flat=True).distinct().order_by('color')
    # Filter out empty colors
    colors = [color for color in colors if color]
    
    # Get material images directly using raw SQL - filter for attachment_type_id = 3 (Product)
    material_images = {}
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ma.material_id, ma.file 
            FROM workshop_app_materialattachment ma 
            WHERE ma.attachment_type_id = 3 
            ORDER BY ma.upload_date DESC
        """)
        rows = cursor.fetchall()
        
        for material_id, file_path in rows:
            if file_path:
                # Create a full URL for the image using MEDIA_URL
                media_url = settings.MEDIA_URL.rstrip('/')
                full_url = f"{media_url}/{file_path}"
                material_images[material_id] = full_url
    
    context = {
        'materials': materials,
        'categories': categories,
        'material_types': material_types,
        'material_images': material_images,
        'colors': colors,  # Add colors to context
    }
    
    return render(request, 'materials/list.html', context)
