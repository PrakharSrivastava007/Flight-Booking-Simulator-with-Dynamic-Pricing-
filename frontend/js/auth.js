// Authentication Management

// Save authentication token
function saveToken(token) {
    localStorage.setItem(STORAGE_KEYS.TOKEN, token);
}

// Get authentication token
function getToken() {
    return localStorage.getItem(STORAGE_KEYS.TOKEN);
}

// Save user data
function saveUser(userData) {
    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(userData));
}

// Get user data
function getUser() {
    const userData = localStorage.getItem(STORAGE_KEYS.USER);
    return userData ? JSON.parse(userData) : null;
}

// Make authenticated API request
async function apiRequest(endpoint, options = {}) {
    const token = getToken();
    
    const defaultHeaders = {
        'Content-Type': 'application/json'
    };
    
    if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}${endpoint}`, config);
        
        // Handle authentication errors
        if (response.status === 401) {
            logout();
            throw new Error('Session expired. Please login again.');
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// Register new user
async function register(userData) {
    try {
        const response = await apiRequest(API_CONFIG.ENDPOINTS.REGISTER, {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        
        showSuccess('Registration successful! Please login.');
        return response;
    } catch (error) {
        showError(error.message || 'Registration failed');
        throw error;
    }
}

// Login user
async function login(email, password) {
    try {
        // FastAPI OAuth2 expects form data
        const formData = new URLSearchParams();
        formData.append('username', email); // FastAPI uses 'username' field
        formData.append('password', password);
        
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.LOGIN}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }
        
        const data = await response.json();
        
        // Save token
        saveToken(data.access_token);
        
        // Fetch and save user profile
        await fetchUserProfile();
        
        showSuccess('Login successful!');
        return data;
    } catch (error) {
        showError(error.message || 'Login failed');
        throw error;
    }
}

// Fetch user profile
async function fetchUserProfile() {
    try {
        const userData = await apiRequest(API_CONFIG.ENDPOINTS.PROFILE);
        saveUser(userData);
        return userData;
    } catch (error) {
        console.error('Failed to fetch user profile:', error);
        throw error;
    }
}

// Update user display (nav bar)
function updateUserDisplay() {
    const user = getUser();
    const userDisplay = document.getElementById('user-display');
    const loginBtn = document.getElementById('login-btn');
    const logoutBtn = document.getElementById('logout-btn');
    
    if (user && userDisplay) {
        userDisplay.textContent = `Hi, ${user.First_name}`;
        userDisplay.style.display = 'inline-block';
        
        if (loginBtn) loginBtn.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'inline-block';
    } else {
        if (userDisplay) userDisplay.style.display = 'none';
        if (loginBtn) loginBtn.style.display = 'inline-block';
        if (logoutBtn) logoutBtn.style.display = 'none';
    }
}

// Initialize user display on page load
document.addEventListener('DOMContentLoaded', () => {
    updateUserDisplay();
});
