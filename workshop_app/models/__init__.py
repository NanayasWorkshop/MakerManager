# Import all models to maintain the same API
from workshop_app.models.material_models import (
    MaterialCategory, MaterialType, Material, 
    AttachmentType, MaterialAttachment
)
from workshop_app.models.machine_models import (
    MachineType, Machine
)
from workshop_app.models.job_models import (
    JobStatus, Job, JobMaterial
)
from workshop_app.models.client_models import (
    Client, ContactPerson
)
from workshop_app.models.user_models import (
    Operator, StaffSettings
)
from workshop_app.models.transaction_models import (
    MaterialTransaction, ScanHistory
)

# Define what's exported when using `from workshop_app.models import *`
__all__ = [
    'MaterialCategory', 'MaterialType', 'Material', 
    'AttachmentType', 'MaterialAttachment',
    'MachineType', 'Machine',
    'JobStatus', 'Job', 'JobMaterial',
    'Client', 'ContactPerson',
    'Operator', 'StaffSettings',
    'MaterialTransaction', 'ScanHistory'
]
