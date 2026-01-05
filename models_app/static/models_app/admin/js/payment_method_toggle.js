(function($) {
    // Wait for Django admin jQuery to be ready
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).ready(function($) {
            function togglePaymentFields() {
                var paymentType = $('#id_payment_type').val();
                var cardFields = $('.card-field').closest('tr, .form-row');
                var mpesaFields = $('.mpesa-field').closest('tr, .form-row');

                if (paymentType === 'card') {
                    cardFields.show();
                    mpesaFields.hide();
                } else if (paymentType === 'mpesa') {
                    cardFields.hide();
                    mpesaFields.show();
                } else {
                    cardFields.hide();
                    mpesaFields.hide();
                }
            }

            // Initial toggle
            togglePaymentFields();

            // Toggle on change
            $('#id_payment_type').change(togglePaymentFields);
        });
    } else {
        // Fallback for when django.jQuery isn't available
        document.addEventListener('DOMContentLoaded', function() {
            function togglePaymentFields() {
                var paymentType = document.getElementById('id_payment_type');
                if (!paymentType) return;

                var paymentTypeValue = paymentType.value;

                // Hide all payment-specific fields first
                var allFields = document.querySelectorAll('.card-field, .mpesa-field');
                allFields.forEach(function(field) {
                    var row = field.closest('tr') || field.closest('.form-row') || field.closest('p');
                    if (row) row.style.display = 'none';
                });

                // Show relevant fields based on payment type
                if (paymentTypeValue === 'card') {
                    var cardFields = document.querySelectorAll('.card-field');
                    cardFields.forEach(function(field) {
                        var row = field.closest('tr') || field.closest('.form-row') || field.closest('p');
                        if (row) row.style.display = '';
                    });
                } else if (paymentTypeValue === 'mpesa') {
                    var mpesaFields = document.querySelectorAll('.mpesa-field');
                    mpesaFields.forEach(function(field) {
                        var row = field.closest('tr') || field.closest('.form-row') || field.closest('p');
                        if (row) row.style.display = '';
                    });
                }
            }

            // Initial toggle
            togglePaymentFields();

            // Toggle on change
            var paymentTypeSelect = document.getElementById('id_payment_type');
            if (paymentTypeSelect) {
                paymentTypeSelect.addEventListener('change', togglePaymentFields);
            }
        });
    }
})(typeof django !== 'undefined' ? django.jQuery : jQuery);
