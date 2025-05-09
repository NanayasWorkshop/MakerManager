# Import views here
from workshop_app.views.machine_views import (
    machine_list,
    machine_detail,
    machine_usage_history,
    get_machine_qr_code,
    add_machine,
    edit_machine,
    start_machine_usage,
    stop_machine_usage
)

# Import job views
from workshop_app.views.job_views import (
    job_list,
    job_detail,
    add_job,
    edit_job,
    get_client_contacts
)
