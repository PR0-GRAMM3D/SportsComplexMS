document.addEventListener('DOMContentLoaded', function() {
    // Get all facility checkboxes
    const facilityCheckboxes = document.querySelectorAll('input[name="membership_facility"]');
    const fixedAmountField = document.getElementById('id_fixed_amount');

    // Check if elements exist before proceeding
    if (!facilityCheckboxes.length || !fixedAmountField) {
        return; // Exit early if elements are missing
    }

    // Use server-provided rates
    const userRates = (typeof serverRates === 'object' && serverRates !== null) ? 
        serverRates : 
        {
            swimming: 1000,
            gym: 1000,
            masterCard: 1500,
            registration: 2000
        };

    // Function to update the price
    async function updatePrice() {
        // Get selected facilities
        const selectedFacilities = Array.from(facilityCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);

        // No facilities selected
        if (selectedFacilities.length === 0) {
            fixedAmountField.value = "0";
            return;
        }

        let monthlyRate = 0;

        // Check if swimming and gym are selected based on their IDs
        const hasSwimming = selectedFacilities.includes('1'); // ID for swimming
        const hasGym = selectedFacilities.includes('2'); // ID for gym

        // Check if we have a Swimming + Gym combination (Master Card)
        if (hasSwimming && hasGym) {
            monthlyRate = userRates.masterCard;
        } else {
            // Otherwise, add individual rates
            if (hasSwimming) {
                monthlyRate += userRates.swimming;
            }
            if (hasGym) {
                monthlyRate += userRates.gym;
            }
        }

        // Add registration fee
        const registrationFee = userRates.registration || 0;
        const totalAmount = monthlyRate + registrationFee;

        // Update the price field
        fixedAmountField.value = totalAmount.toString();
    }

    // Add event listeners to all checkboxes
    facilityCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updatePrice);
    });

    // Initialize price on page load
    updatePrice();
});