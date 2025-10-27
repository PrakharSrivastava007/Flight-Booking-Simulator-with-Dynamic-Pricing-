// Utility Functions

// Format date to YYYY-MM-DD
function formatDate(date) {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}


// Format datetime to readable format

function formatDateTime(datetime) {
    const date = new Date(datetime);
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('en-IN', options);
}


// Format time only

function formatTime(datetime) {
    const date = new Date(datetime);
    return date.toLocaleTimeString('en-IN', {
        hour: '2-digit',
        minute: '2-digit'
    });
}


// Calculate duration in readable format
function formatDuration(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
}


// Format currency in Indian Rupees
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

// Show loading spinner

function showLoading(containerId = 'loading-spinner') {
    const spinner = document.getElementById(containerId);
    if (spinner) {
        spinner.style.display = 'flex';
    }
}


// Hide loading spinner
function hideLoading(containerId = 'loading-spinner') {
    const spinner = document.getElementById(containerId);
    if (spinner) {
        spinner.style.display = 'none';
    }
}


// Show error message

function showError(message, containerId = 'error-message') {
    const errorDiv = document.getElementById(containerId);
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    } else {
        alert(message);
    }
}


// Show success message

function showSuccess(message, containerId = 'success-message') {
    const successDiv = document.getElementById(containerId);
    if (successDiv) {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            successDiv.style.display = 'none';
        }, 3000);
    } else {
        alert(message);
    }
}

// Get query parameter from URL
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}


// Set query parameter in URL
function setQueryParam(param, value) {
    const url = new URL(window.location);
    url.searchParams.set(param, value);
    window.history.pushState({}, '', url);
}


// Validate email format

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}


// Validate phone number (Indian format)
function validatePhone(phone) {
    const re = /^[+]?[0-9]{10,13}$/;
    return re.test(phone);
}


// Debounce function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Generate random PNR (for demo/placeholder)

function generateRandomPNR() {
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const numbers = '0123456789';
    let pnr = '';
    for (let i = 0; i < 3; i++) {
        pnr += letters.charAt(Math.floor(Math.random() * letters.length));
    }
    for (let i = 0; i < 3; i++) {
        pnr += numbers.charAt(Math.floor(Math.random() * numbers.length));
    }
    return pnr;
}

// Scroll to top smoothly
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}


// Get min date for flight search (today)

function getMinDate() {
    return formatDate(new Date());
}


// Get max date for flight search (1 year from today)
 
function getMaxDate() {
    const date = new Date();
    date.setFullYear(date.getFullYear() + 1);
    return formatDate(date);
}


// Check if user is logged in

function isLoggedIn() {
    return !!localStorage.getItem(STORAGE_KEYS.TOKEN);
}


// Redirect to login if not authenticated

function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}


// Logout user

function logout() {
    localStorage.removeItem(STORAGE_KEYS.TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER);
    window.location.href = 'index.html';
}
