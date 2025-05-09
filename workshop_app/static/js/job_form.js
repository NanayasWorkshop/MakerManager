/**
 * Job Form JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    setupFormValidation();
    
    // Client change handler
    setupClientChangeHandler();
    
    // Percent slider sync with input
    setupPercentSlider();
});

// Setup form validation
function setupFormValidation() {
    const jobForm = document.getElementById('addJobForm') || 
                    document.getElementById('editJobForm');
    
    if (jobForm) {
        jobForm.addEventListener('submit', function(event) {
            let isValid = true;
            
            // Validate required fields
            const requiredFields = jobForm.querySelectorAll('[required]');
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            // Validate date inputs
            const startDate = document.getElementById('start_date');
            const expectedCompletion = document.getElementById('expected_completion');
            const deadline = document.getElementById('deadline');
            
            if (startDate && expectedCompletion && 
                startDate.value && expectedCompletion.value &&
                new Date(startDate.value) > new Date(expectedCompletion.value)) {
                isValid = false;
                expectedCompletion.classList.add('is-invalid');
                alert('Expected completion date cannot be earlier than start date');
            }
            
            if (startDate && deadline && 
                startDate.value && deadline.value &&
                new Date(startDate.value) > new Date(deadline.value)) {
                isValid = false;
                deadline.classList.add('is-invalid');
                alert('Deadline cannot be earlier than start date');
            }
            
            if (!isValid) {
                event.preventDefault();
                alert('Please correct the errors in the form before submitting.');
            }
        });
        
        // Remove invalid class on input
        const formInputs = jobForm.querySelectorAll('input, select, textarea');
        formInputs.forEach(input => {
            input.addEventListener('input', function() {
                this.classList.remove('is-invalid');
            });
        });
    }
}

// Setup client change handler to populate contact persons
function setupClientChangeHandler() {
    const clientSelect = document.getElementById('client');
    const contactPersonSelect = document.getElementById('contact_person');
    
    if (clientSelect && contactPersonSelect) {
        clientSelect.addEventListener('change', function() {
            const clientId = this.value;
            
            if (clientId) {
                // Enable contact person select
                contactPersonSelect.disabled = false;
                
                // Clear current options except the first one
                while (contactPersonSelect.options.length > 1) {
                    contactPersonSelect.remove(1);
                }
                
                // Fetch contact persons for selected client
                fetch(`/api/clients/${clientId}/contacts/`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            data.contacts.forEach(contact => {
                                const option = document.createElement('option');
                                option.value = contact.id;
                                option.textContent = contact.name;
                                contactPersonSelect.appendChild(option);
                            });
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching contacts:', error);
                    });
            } else {
                // Disable contact person select if no client selected
                contactPersonSelect.disabled = true;
                contactPersonSelect.value = '';
            }
        });
    }
}

// Setup percent complete slider sync with input
function setupPercentSlider() {
    const percentSlider = document.getElementById('percent_complete_slider');
    const percentInput = document.getElementById('percent_complete');
    
    if (percentSlider && percentInput) {
        percentSlider.addEventListener('input', function() {
            percentInput.value = this.value;
        });
        
        percentInput.addEventListener('input', function() {
            percentSlider.value = this.value;
        });
    }
}
