// API Configuration
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000',
    ENDPOINTS: {
        // Auth
        REGISTER: '/api/v1/users/register',
        LOGIN: '/api/v1/users/login',
        PROFILE: '/api/v1/users/me',
        
        // Flights
        SEARCH_FLIGHTS: '/api/v1/flights/search',
        GET_FLIGHT: '/api/v1/flights',
        LIST_AIRLINES: '/api/v1/flights/airlines/list',
        LIST_AIRPORTS: '/api/v1/flights/airports/list',
        
        // Bookings
        CREATE_BOOKING: '/api/v1/bookings/create',
        CONFIRM_BOOKING: '/api/v1/bookings/{pnr}/confirm',
        MY_BOOKINGS: '/api/v1/bookings/my-bookings',
        GET_BOOKING: '/api/v1/bookings/{pnr}',
        CANCEL_BOOKING: '/api/v1/bookings/{pnr}/cancel',
        
        // Price History
        PRICE_HISTORY: '/api/v1/price-history/{flight_id}',
        
        // External
        EXTERNAL_FLIGHTS: '/api/v1/external/flights/fetch'
    }
};

// Storage keys
const STORAGE_KEYS = {
    TOKEN: 'auth_token',
    USER: 'user_data',
    SEARCH_PARAMS: 'search_params',
    SELECTED_FLIGHT: 'selected_flight',
    BOOKING_DATA: 'booking_data'
};

// Indian cities and airports
const INDIAN_AIRPORTS = [
    { code: 'DEL', city: 'New Delhi', name: 'Indira Gandhi International Airport' },
    { code: 'BOM', city: 'Mumbai', name: 'Chhatrapati Shivaji Maharaj International' },
    { code: 'BLR', city: 'Bangalore', name: 'Kempegowda International Airport' },
    { code: 'MAA', city: 'Chennai', name: 'Chennai International Airport' },
    { code: 'CCU', city: 'Kolkata', name: 'Netaji Subhas Chandra Bose International' },
    { code: 'HYD', city: 'Hyderabad', name: 'Rajiv Gandhi International Airport' },
    { code: 'PNQ', city: 'Pune', name: 'Pune Airport' },
    { code: 'AMD', city: 'Ahmedabad', name: 'Sardar Vallabhbhai Patel International' },
    { code: 'GOI', city: 'Goa', name: 'Goa International Airport' },
    { code: 'COK', city: 'Kochi', name: 'Cochin International Airport' },
    { code: 'JAI', city: 'Jaipur', name: 'Jaipur International Airport' },
    { code: 'LKO', city: 'Lucknow', name: 'Chaudhary Charan Singh International' }
];

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API_CONFIG, STORAGE_KEYS, INDIAN_AIRPORTS };
}
