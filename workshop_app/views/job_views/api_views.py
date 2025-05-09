"""
API endpoints for job management.
"""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from workshop_app.models import Client, ContactPerson

@login_required
def get_client_contacts(request, client_id):
    """API endpoint to get contact persons for a client"""
    client = get_object_or_404(Client, id=client_id)
    contacts = ContactPerson.objects.filter(client=client).order_by('name')
    
    # Create contact list for JSON response
    contact_list = []
    for contact in contacts:
        contact_list.append({
            'id': contact.id,
            'name': contact.name,
            'position': contact.position,
            'is_primary': contact.primary_contact
        })
    
    return JsonResponse({
        'success': True,
        'contacts': contact_list
    })
