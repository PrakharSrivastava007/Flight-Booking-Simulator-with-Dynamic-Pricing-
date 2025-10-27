// Booking Page Logic

let selectedFlight = null;
let searchParams = null;
let passengerCount = 0;
let currentPassengerData = [];

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    // Check if user is logged in
    if (!requireAuth()) return;
    
    updateUserDisplay();
    
    // Get selected flight
    const flightData = localStorage.getItem(STORAGE_KEYS.SELECTED_FLIGHT);
    const params = localStorage.getItem(STORAGE_KEYS.SEARCH_PARAMS);
    
    if (!flightData || !params) {
        showError('No flight selected');
        setTimeout(() => window.location.href = 'index.html', 2000);
        return;
    }
    
    selectedFlight = JSON.parse(flightData);
    searchParams = JSON.parse(params);
    passengerCount = searchParams.passengers;
    
    // Initialize page
    displayFlightSummary();
    generatePassengerForms();
    prefillContactInfo();
    calculateFares();
});

// Display flight summary
function displayFlightSummary() {
    const summary = `
        <div class="flight-summary-card">
            <div class="flight-route">
                <div class="route-city">
                    <div class="city-name">${selectedFlight.origin_code}</div>
                    <div class="city-code">${selectedFlight.origin_city}</div>
                </div>
                <div class="route-arrow">
                    <i class="fas fa-plane"></i>
                </div>
                <div class="route-city">
                    <div class="city-name">${selectedFlight.destination_code}</div>
                    <div class="city-code">${selectedFlight.destination_city}</div>
                </div>
            </div>
            <div class="flight-info">
                <div class="airline-name">${selectedFlight.airline_name}</div>
                <div class="flight-details-text">${selectedFlight.Flight_Number}</div>
                <div class="flight-details-text">${formatDateTime(selectedFlight.Departure_Time)}</div>
                <div class="flight-details-text">${formatDuration(selectedFlight.Duration)}</div>
                <div class="flight-details-text">${selectedFlight.seat_class.toUpperCase()}</div>
            </div>
        </div>
    `;
    
    document.getElementById('flight-summary').innerHTML = summary;
}

// Generate passenger forms
function generatePassengerForms() {
    const container = document.getElementById('passengers-container');
    container.innerHTML = '';
    
    for (let i = 0; i < passengerCount; i++) {
        container.innerHTML += createPassengerForm(i);
    }
    
    // Show add button if less than 9 passengers
    if (passengerCount < 9) {
        document.querySelector('.btn-add-passenger').style.display = 'block';
    }
}

// Create passenger form HTML
function createPassengerForm(index) {
    return `
        <div class="passenger-form" id="passenger-${index}">
            <div class="passenger-header">
                <h4>Passenger ${index + 1}</h4>
                ${index > 0 ? `<button type="button" class="btn-remove-passenger" onclick="removePassenger(${index})">Remove</button>` : ''}
            </div>
            
            <div class="form-grid">
                <div class="form-group">
                    <label>First Name <span class="required">*</span></label>
                    <input type="text" id="firstname-${index}" placeholder="First Name" required>
                </div>
                
                <div class="form-group">
                    <label>Last Name <span class="required">*</span></label>
                    <input type="text" id="lastname-${index}" placeholder="Last Name" required>
                </div>
                
                <div class="form-group">
                    <label>Date of Birth <span class="required">*</span></label>
                    <input type="date" id="dob-${index}" max="${formatDate(new Date())}" required>
                </div>
                
                <div class="form-group">
                    <label>Gender <span class="required">*</span></label>
                    <select id="gender-${index}" required>
                        <option value="">Select Gender</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Nationality <span class="required">*</span></label>
                    <input type="text" id="nationality-${index}" value="India" required>
                </div>
                
                <div class="form-group">
                    <label>Passport Number</label>
                    <input type="text" id="passport-${index}" placeholder="Optional">
                </div>
                
                <div class="form-group">
                    <label>Email <span class="required">*</span></label>
                    <input type="email" id="email-${index}" placeholder="passenger@example.com" required>
                </div>
                
                <div class="form-group">
                    <label>Phone <span class="required">*</span></label>
                    <input type="tel" id="phone-${index}" placeholder="+91 9876543210" required>
                </div>
            </div>
        </div>
    `;
}

// Add passenger
function addPassenger() {
    if (passengerCount >= 9) {
        showError('Maximum 9 passengers allowed');
        return;
    }
    
    passengerCount++;
    const container = document.getElementById('passengers-container');
    container.innerHTML += createPassengerForm(passengerCount - 1);
    
    if (passengerCount >= 9) {
        document.querySelector('.btn-add-passenger').style.display = 'none';
    }
    
    calculateFares();
}

// Remove passenger
function removePassenger(index) {
    if (passengerCount <= 1) {
        showError('At least one passenger required');
        return;
    }
    
    document.getElementById(`passenger-${index}`).remove();
    passengerCount--;
    
    // Renumber remaining passengers
    const forms = document.querySelectorAll('.passenger-form');
    forms.forEach((form, idx) => {
        form.querySelector('h4').textContent = `Passenger ${idx + 1}`;
    });
    
    document.querySelector('.btn-add-passenger').style.display = 'block';
    calculateFares();
}

// Prefill contact info
function prefillContactInfo() {
    const user = getUser();
    if (user) {
        document.getElementById('contact-email').value = user.Email || '';
        document.getElementById('contact-phone').value = user.Phone || '';
    }
}

// Calculate fares
function calculateFares() {
    const baseFare = selectedFlight.dynamic_price;
    const totalBase = baseFare * passengerCount;
    const discount = (selectedFlight.base_price - selectedFlight.dynamic_price) * passengerCount;
    const taxes = totalBase * 0.05; // 5% taxes
    const total = totalBase + taxes;
    
    document.getElementById('base-fare').textContent = formatCurrency(totalBase);
    document.getElementById('taxes').textContent = formatCurrency(taxes);
    document.getElementById('total-amount').textContent = formatCurrency(total);
    document.getElementById('passengers-info').textContent = `${passengerCount} Passenger(s)`;
    
    // Show discount if applicable
    if (discount > 0) {
        document.getElementById('discount-row').style.display = 'flex';
        document.getElementById('discount-amount').textContent = '-' + formatCurrency(discount);
    }
    
    // Display price breakdown
    if (selectedFlight.price_breakdown) {
        displayPriceBreakdown(selectedFlight.price_breakdown);
    }
}

// Display price breakdown
function displayPriceBreakdown(breakdown) {
    const container = document.getElementById('price-breakdown');
    
    const factors = [
        { label: 'Seat Availability Factor', value: breakdown.seat_factor },
        { label: 'Time to Departure', value: breakdown.time_factor },
        { label: 'Demand Factor', value: breakdown.demand_factor },
        { label: 'Seasonal Factor', value: breakdown.seasonal_factor },
        { label: 'Weekend Premium', value: breakdown.weekend_factor },
        { label: 'Peak Hour Factor', value: breakdown.peak_hour_factor }
    ];
    
    container.innerHTML = factors.map(f => `
        <div class="breakdown-item">
            <span class="breakdown-label">${f.label}:</span>
            <span class="breakdown-value">${f.value > 0 ? '+' : ''}${(f.value * 100).toFixed(1)}%</span>
        </div>
    `).join('');
}

// Toggle price breakdown
function toggleBreakdown() {
    const breakdown = document.getElementById('price-breakdown');
    const icon = document.querySelector('.price-breakdown-toggle i');
    
    if (breakdown.style.display === 'none') {
        breakdown.style.display = 'block';
        icon.classList.replace('fa-chevron-down', 'fa-chevron-up');
    } else {
        breakdown.style.display = 'none';
        icon.classList.replace('fa-chevron-up', 'fa-chevron-down');
    }
}

// Collect passenger data
function collectPassengerData() {
    const passengers = [];
    
    for (let i = 0; i < passengerCount; i++) {
        const passenger = {
            First_name: document.getElementById(`firstname-${i}`)?.value.trim(),
            Last_name: document.getElementById(`lastname-${i}`)?.value.trim(),
            Date_of_birth: document.getElementById(`dob-${i}`)?.value,
            Gender: document.getElementById(`gender-${i}`)?.value,
            Nationality: document.getElementById(`nationality-${i}`)?.value.trim(),
            Passport_number: document.getElementById(`passport-${i}`)?.value.trim() || null,
            Email: document.getElementById(`email-${i}`)?.value.trim(),
            Phone: document.getElementById(`phone-${i}`)?.value.trim()
        };
        
        // Validation
        if (!passenger.First_name || !passenger.Last_name || !passenger.Date_of_birth || 
            !passenger.Gender || !passenger.Email || !passenger.Phone) {
            throw new Error(`Please fill all required fields for Passenger ${i + 1}`);
        }
        
        if (!validateEmail(passenger.Email)) {
            throw new Error(`Invalid email for Passenger ${i + 1}`);
        }
        
        if (!validatePhone(passenger.Phone)) {
            throw new Error(`Invalid phone number for Passenger ${i + 1}`);
        }
        
        passengers.push(passenger);
    }
    
    return passengers;
}

// Proceed to payment
async function proceedToPayment() {
    try {
        // Validate terms checkbox
        if (!document.getElementById('terms-checkbox').checked) {
            showError('Please accept the terms and conditions');
            return;
        }
        
        // Collect passenger data
        const passengers = collectPassengerData();
        
        // Validate contact info
        const contactEmail = document.getElementById('contact-email').value.trim();
        const contactPhone = document.getElementById('contact-phone').value.trim();
        
        if (!validateEmail(contactEmail)) {
            showError('Invalid contact email');
            return;
        }
        
        if (!validatePhone(contactPhone)) {
            showError('Invalid contact phone number');
            return;
        }
        
        showLoading();
        
        // Create booking
        const bookingData = {
            FlightID: selectedFlight.FlightID,
            Seat_class: selectedFlight.seat_class,
            passengers: passengers
        };
        
        const response = await apiRequest(API_CONFIG.ENDPOINTS.CREATE_BOOKING, {
            method: 'POST',
            body: JSON.stringify(bookingData)
        });
        
        hideLoading();
        
        // Save booking data
        localStorage.setItem(STORAGE_KEYS.BOOKING_DATA, JSON.stringify(response));
        
        showSuccess('Booking created successfully!');
        
        // Redirect to payment
        setTimeout(() => {
            window.location.href = 'payment.html';
        }, 1000);
        
    } catch (error) {
        hideLoading();
        showError(error.message || 'Failed to create booking');
    }
}
