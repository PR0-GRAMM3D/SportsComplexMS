// Script to handle booking pricing and bowling-specific fields
document.addEventListener('DOMContentLoaded', function() {
    const facilitySelect = document.getElementById('id_booking_facility');
    const bowlingFields = document.getElementById('bowling-fields');
    const numberPlayers = document.getElementById('id_number_of_players');
    const mixedGender = document.getElementById('id_is_mixed_gender');
    const totalAmount = document.getElementById('id_total_amount');
    const alleysNeeded = document.getElementById('id_alleys_needed');
    
    // Show/hide bowling fields based on facility selection
    function toggleBowlingFields() {
        if (!facilitySelect) return;
        
        const selectedOption = facilitySelect.options[facilitySelect.selectedIndex];
        const facilityName = selectedOption ? selectedOption.text.toLowerCase() : '';
        
        if (facilityName.includes('bowling')) {
            // Show bowling fields
            if (bowlingFields) bowlingFields.style.display = 'block';
            // Calculate price when bowling is selected
            calculatePrice();
        } else {
            // Hide bowling fields
            if (bowlingFields) bowlingFields.style.display = 'none';
            if (numberPlayers) numberPlayers.value = '';
            if (mixedGender) mixedGender.checked = false;
            
            // Set price to 0 for free facilities
            if (totalAmount) totalAmount.value = 0;
        }
    }
    
    // Calculate price based on number of players
    function calculatePrice() {
        if (!totalAmount || !numberPlayers) return;
        
        const players = parseInt(numberPlayers.value) || 0;
        let price = 0;
        let alleys = 1;
        
        // calculating the player-based price
        if (players > 0) {
            price = 200 * players; // Rs. 200 per player
        }
        
        // Separately track alleys needed for availability and logistics
        if (mixedGender && mixedGender.checked) {
            alleys = 2; // Always 2 alleys for mixed groups BUSINESS RULE
        } else if (players > 4) {
            alleys = 2; // 2 alleys for more than 4 players
        }
        
        alleysNeeded.value = alleys;
        totalAmount.value = price;
    }
    
    // Add event listeners
    if (facilitySelect) facilitySelect.addEventListener('change', toggleBowlingFields);
    if (numberPlayers) numberPlayers.addEventListener('input', calculatePrice);
    if (mixedGender) mixedGender.addEventListener('change', calculatePrice);
    
    // Initialize on page load
    toggleBowlingFields();
});