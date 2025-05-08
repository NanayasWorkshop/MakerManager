# Re-export the forms from material_forms
from workshop_app.forms.material_forms import MaterialFilterForm, MaterialForm, MaterialTransactionForm, MaterialRestockForm

# Re-export the original forms
from workshop_app.forms.base_forms import ManualEntryForm, LoginForm

# Re-export machine forms
from workshop_app.forms.machine_forms import MachineFilterForm, MachineForm, MachineUsageForm, MachineStopUsageForm
