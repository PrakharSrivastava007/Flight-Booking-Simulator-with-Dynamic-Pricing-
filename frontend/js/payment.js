// Payment Page Logic

let bookingData = null;
let timerInterval = null;
let timeRemaining = 15 * 60; // 15 minutes in seconds

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    
    updateUserDisplay();
    
    // Get booking data
    const data = localStorage.getItem(STORAGE_KEYS.BOOKING_DATA);
    if (!data) {
        showError('No booking found');
        setTimeout(() => window.location.href = 'index.html', 2000);
        return;
    }
    
    bookingData = JSON.parse(data);
    
    // Initialize page
    displayBookingSummary();
    startTimer();
    setupPaymentMethodSwitch();
});

// Display booking summary
function displayBookingSummary() {
    const summary = `
        <div class="summary-item">
            <strong>Flight:</strong> ${bookingData.flight_details.flight_number}
        </div>
        <div class="summary-item">
            <strong>Route:</strong> ${bookingData.flight_details.origin} → ${bookingData.flight_details.destination}
        </div>
        <div class="summary-item">
            <strong>Date:</strong> ${formatDate(bookingData.flight_details.departure)}
        </div>
        <div class="summary-item">
            <strong>Passengers:</strong> ${bookingData.Num_passengers}
        </div>
        <div class="summary-item">
            <strong>Class:</strong> ${bookingData.Seat_class.toUpperCase()}
        </div>
    `;
    
    document.getElementById('booking-summary').innerHTML = summary;
    document.getElementById('total-amount').textContent = formatCurrency(bookingData.Total_price);
    document.getElementById('pay-amount').textContent = formatCurrency(bookingData.Total_price);
    document.getElementById('pnr-number').textContent = bookingData.pnr;
}

// Start countdown timer
function startTimer() {
    updateTimerDisplay();
    
    timerInterval = setInterval(() => {
        timeRemaining--;
        
        if (timeRemaining <= 0) {
            clearInterval(timerInterval);
            handleExpiry();
        }
        
        updateTimerDisplay();
    }, 1000);
}

// Update timer display
function updateTimerDisplay() {
    const minutes = Math.floor(timeRemaining / 60);
    const seconds = timeRemaining % 60;
    const display = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    document.getElementById('timer').textContent = display;
    
    // Change color when time is running out
    const timerElement = document.querySelector('.booking-timer');
    if (timeRemaining < 300) { // Less than 5 minutes
        timerElement.style.background = 'linear-gradient(135deg, #ff9800, #f44336)';
    }
}

// Handle booking expiry
function handleExpiry() {
    showError('Booking expired. Please try again.');
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 3000);
}

// Setup payment method switching
function setupPaymentMethodSwitch() {
    document.querySelectorAll('input[name="payment-method"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            // Hide all forms
            document.querySelectorAll('.payment-form').forEach(form => {
                form.classList.remove('active');
            });
            
            // Show selected form
            const method = e.target.value;
            const formId = method === 'credit_card' ? 'card-form' : 
                          method === 'netbanking' ? 'netbanking-form' :
                          method === 'wallet' ? 'wallet-form' : 'upi-form';
            
            document.getElementById(formId).classList.add('active');
        });
    });
}

// Process payment
async function processPayment() {
    try {
        const paymentMethod = document.querySelector('input[name="payment-method"]:checked').value;
        
        // Basic validation based on payment method
        if (paymentMethod === 'upi') {
            const upiId = document.getElementById('upi-id').value.trim();
            if (!upiId) {
                showError('Please enter UPI ID');
                return;
            }
        } else if (paymentMethod === 'credit_card') {
            const cardNumber = document.getElementById('card-number').value.trim();
            const cardExpiry = document.getElementById('card-expiry').value.trim();
            const cardCvv = document.getElementById('card-cvv').value.trim();
            const cardName = document.getElementById('card-name').value.trim();
            
            if (!cardNumber || !cardExpiry || !cardCvv || !cardName) {
                showError('Please fill all card details');
                return;
            }
        } else if (paymentMethod === 'netbanking') {
            const bank = document.getElementById('bank-select').value;
            if (!bank) {
                showError('Please select a bank');
                return;
            }
        } else if (paymentMethod === 'wallet') {
            const wallet = document.getElementById('wallet-select').value;
            if (!wallet) {
                showError('Please select a wallet');
                return;
            }
        }
        
        showLoading();
        
        // Simulate payment processing delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Confirm booking with backend
        const endpoint = API_CONFIG.ENDPOINTS.CONFIRM_BOOKING.replace('{pnr}', bookingData.pnr);
        const response = await apiRequest(endpoint, {
            method: 'POST',
            body: JSON.stringify({
                payment_method: paymentMethod
            })
        });
        
        hideLoading();
        clearInterval(timerInterval);
        
        // Save confirmed booking
        localStorage.setItem(STORAGE_KEYS.BOOKING_DATA, JSON.stringify(response));
        
        showSuccess('Payment successful!');
        
        // Redirect to confirmation
        setTimeout(() => {
            window.location.href = 'confirmation.html';
        }, 1500);
        
    } catch (error) {
        hideLoading();
        showError(error.message || 'Payment failed. Please try again.');
    }
}

// Format card number input
document.getElementById('card-number')?.addEventListener('input', (e) => {
    let value = e.target.value.replace(/\s/g, '');
    let formatted = value.match(/.{1,4}/g)?.join(' ') || value;
    e.target.value = formatted;
});

// Format expiry date input
document.getElementById('card-expiry')?.addEventListener('input', (e) => {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length >= 2) {
        value = value.slice(0, 2) + '/' + value.slice(2, 4);
    }
    e.target.value = value;
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (timerInterval) {
        clearInterval(timerInterval);
    }
});
