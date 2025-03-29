// Main JavaScript for Diabetes Tracker

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    
    // Set up date picker defaults
    const today = new Date();
    const dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(input => {
        // Set max date to today (prevent future dates)
        if (!input.getAttribute('max')) {
            input.setAttribute('max', today.toISOString().split('T')[0]);
        }
    });
    
    // Confirmation for delete actions
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Reading category highlight
    const glucoseReadings = document.querySelectorAll('.glucose-value');
    glucoseReadings.forEach(reading => {
        const value = parseInt(reading.textContent);
        if (value > 180) {
            reading.classList.add('reading-high');
        } else if (value < 70) {
            reading.classList.add('reading-low');
        } else {
            reading.classList.add('reading-normal');
        }
    });
    
    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Quick date range selector for analytics
    const dateRangeSelector = document.getElementById('date-range-selector');
    if (dateRangeSelector) {
        dateRangeSelector.addEventListener('change', function() {
            const value = this.value;
            
            if (value === 'custom') {
                document.getElementById('custom-date-range').style.display = 'flex';
            } else {
                document.getElementById('custom-date-range').style.display = 'none';
                // Auto-submit form when selecting a preset range
                this.form.submit();
            }
        });
    }
    
    // Print functionality
    const printButtons = document.querySelectorAll('.print-button');
    printButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    });
    
    // Show/hide additional form fields based on selection
    const toggleFields = document.querySelectorAll('[data-toggle-field]');
    toggleFields.forEach(field => {
        field.addEventListener('change', function() {
            const targetId = this.getAttribute('data-toggle-field');
            const targetElement = document.getElementById(targetId);
            
            if (this.checked || this.value === 'true' || this.value === '1') {
                targetElement.style.display = 'block';
            } else {
                targetElement.style.display = 'none';
            }
        });
        
        // Trigger change event to set initial state
        field.dispatchEvent(new Event('change'));
    });
    
    // Tooltips initialization
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
    
    // Mobile menu toggle
    const menuToggle = document.querySelector('.navbar-toggler');
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            document.querySelector('.navbar-collapse').classList.toggle('show');
        });
    }
}); 