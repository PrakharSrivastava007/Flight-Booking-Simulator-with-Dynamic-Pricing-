// Flight Search Results Logic

let allFlights = [];
let filteredFlights = [];
let searchParams = {};

// Initialize page
document.addEventListener('DOMContentLoaded', async () => {
    updateUserDisplay();
    
    // Get search parameters
    const params = localStorage.getItem(STORAGE_KEYS.SEARCH_PARAMS);
    if (!params) {
        window.location.href = 'index.html';
        return;
    }
    
    searchParams = JSON.parse(params);
    displaySearchSummary();
    
    // Search flights
    await searchFlights();
    
    // Setup filters
    setupFilters();
});

// Display search summary
function displaySearchSummary() {
    const originAirport = INDIAN_AIRPORTS.find(a => a.code === searchParams.origin);
    const destAirport = INDIAN_AIRPORTS.find(a => a.code === searchParams.destination);
    
    document.getElementById('route-display').textContent = 
        `${originAirport.city} → ${destAirport.city}`;
    
    document.getElementById('date-display').textContent = 
        `${formatDate(searchParams.departure_date)} • ${searchParams.passengers} Passenger(s) • ${searchParams.seat_class}`;
}

// Search flights via API
async function searchFlights() {
    showLoading();
    
    try {
        const response = await apiRequest(API_CONFIG.ENDPOINTS.SEARCH_FLIGHTS, {
            method: 'POST',
            body: JSON.stringify(searchParams)
        });
        
        allFlights = response;
        filteredFlights = [...allFlights];
        
        hideLoading();
        
        if (allFlights.length === 0) {
            showNoResults();
        } else {
            displayFlights(filteredFlights);
            populateAirlineFilters();
        }
        
    } catch (error) {
        hideLoading();
        showError(error.message || 'Failed to fetch flights');
        showNoResults();
    }
}

// Display flights
function displayFlights(flights) {
    const container = document.getElementById('flights-container');
    const noResults = document.getElementById('no-results');
    const resultsCount = document.getElementById('results-count');
    
    if (flights.length === 0) {
        showNoResults();
        return;
    }
    
    noResults.style.display = 'none';
    resultsCount.textContent = `${flights.length} Flight(s) Found`;
    
    container.innerHTML = flights.map(flight => createFlightCard(flight)).join('');
}

// Create flight card HTML
function createFlightCard(flight) {
    const priceDiscount = ((flight.base_price - flight.dynamic_price) / flight.base_price * 100).toFixed(0);
    const showDiscount = priceDiscount > 0;
    
    return `
        <div class="flight-card" onclick="selectFlight(${flight.FlightID})">
            <div class="flight-header">
                <div class="airline-info">
                    <div class="airline-logo">${flight.airline_code}</div>
                    <div class="airline-details">
                        <h4>${flight.airline_name}</h4>
                        <div class="flight-number">${flight.Flight_Number}</div>
                    </div>
                </div>
                <div class="flight-class">${flight.seat_class}</div>
            </div>
            
            <div class="flight-details">
                <div class="flight-time">
                    <div class="time">${formatTime(flight.Departure_Time)}</div>
                    <div class="location">${flight.origin_code}</div>
                    <div class="location">${flight.origin_city}</div>
                </div>
                
                <div class="flight-duration">
                    <div class="duration-text">${formatDuration(flight.Duration)}</div>
                    <div class="duration-bar"></div>
                    <div class="duration-text">Non-stop</div>
                </div>
                
                <div class="flight-time">
                    <div class="time">${formatTime(flight.Arrival_Time)}</div>
                    <div class="location">${flight.destination_code}</div>
                    <div class="location">${flight.destination_city}</div>
                </div>
            </div>
            
            <div class="flight-footer">
                <div class="info-section">
                    ${flight.seats_available < 10 ? 
                        `<div class="seats-left">⚠️ Only ${flight.seats_available} seats left!</div>` : 
                        `<div class="seats-left">${flight.seats_available} seats available</div>`
                    }
                </div>
                
                <div class="price-section">
                    ${showDiscount ? 
                        `<div class="base-price">${formatCurrency(flight.base_price)}</div>` : 
                        ''
                    }
                    <div class="final-price">
                        ${formatCurrency(flight.dynamic_price)}
                        ${showDiscount ? 
                            `<span class="price-badge">${priceDiscount}% OFF</span>` : 
                            ''
                        }
                    </div>
                </div>
                
                <button class="btn-book" onclick="event.stopPropagation(); bookFlight(${flight.FlightID})">
                    Book Now <i class="fas fa-arrow-right"></i>
                </button>
            </div>
        </div>
    `;
}

// Select flight (view details)
function selectFlight(flightId) {
    const flight = allFlights.find(f => f.FlightID === flightId);
    if (flight) {
        localStorage.setItem(STORAGE_KEYS.SELECTED_FLIGHT, JSON.stringify(flight));
        window.location.href = `flight-details.html?id=${flightId}`;
    }
}

// Book flight directly
function bookFlight(flightId) {
    if (!isLoggedIn()) {
        showError('Please login to book flights');
        setTimeout(() => {
            window.location.href = `login.html?redirect=results.html`;
        }, 1500);
        return;
    }
    
    const flight = allFlights.find(f => f.FlightID === flightId);
    if (flight) {
        localStorage.setItem(STORAGE_KEYS.SELECTED_FLIGHT, JSON.stringify(flight));
        window.location.href = 'booking.html';
    }
}

// Populate airline filters
function populateAirlineFilters() {
    const airlines = [...new Set(allFlights.map(f => f.airline_name))];
    const container = document.getElementById('airline-filters');
    
    container.innerHTML = airlines.map(airline => `
        <label class="checkbox-label">
            <input type="checkbox" value="${airline}" class="airline-filter" checked>
            <span>${airline}</span>
        </label>
    `).join('');
    
    // Add event listeners
    document.querySelectorAll('.airline-filter').forEach(checkbox => {
        checkbox.addEventListener('change', applyFilters);
    });
}

// Setup filters
function setupFilters() {
    // Sort options
    document.querySelectorAll('input[name="sort"]').forEach(radio => {
        radio.addEventListener('change', applyFilters);
    });
    
    // Price range
    const priceRange = document.getElementById('price-range');
    const priceValue = document.getElementById('price-value');
    
    priceRange.addEventListener('input', (e) => {
        priceValue.textContent = formatCurrency(e.target.value);
    });
    
    priceRange.addEventListener('change', applyFilters);
    
    // Time filters
    document.querySelectorAll('.time-filter').forEach(checkbox => {
        checkbox.addEventListener('change', applyFilters);
    });
}

// Apply all filters
function applyFilters() {
    filteredFlights = [...allFlights];
    
    // Filter by airline
    const selectedAirlines = Array.from(document.querySelectorAll('.airline-filter:checked'))
        .map(cb => cb.value);
    
    if (selectedAirlines.length > 0) {
        filteredFlights = filteredFlights.filter(f => 
            selectedAirlines.includes(f.airline_name)
        );
    }
    
    // Filter by price
    const maxPrice = parseInt(document.getElementById('price-range').value);
    filteredFlights = filteredFlights.filter(f => f.dynamic_price <= maxPrice);
    
    // Filter by departure time
    const selectedTimes = Array.from(document.querySelectorAll('.time-filter:checked'))
        .map(cb => cb.value);
    
    if (selectedTimes.length > 0) {
        filteredFlights = filteredFlights.filter(f => {
            const hour = new Date(f.Departure_Time).getHours();
            
            if (selectedTimes.includes('morning') && hour >= 6 && hour < 12) return true;
            if (selectedTimes.includes('afternoon') && hour >= 12 && hour < 18) return true;
            if (selectedTimes.includes('evening') && hour >= 18 && hour < 24) return true;
            
            return false;
        });
    }
    
    // Sort
    const sortBy = document.querySelector('input[name="sort"]:checked').value;
    
    if (sortBy === 'price') {
        filteredFlights.sort((a, b) => a.dynamic_price - b.dynamic_price);
    } else if (sortBy === 'duration') {
        filteredFlights.sort((a, b) => a.Duration - b.Duration);
    } else if (sortBy === 'departure_time') {
        filteredFlights.sort((a, b) => 
            new Date(a.Departure_Time) - new Date(b.Departure_Time)
        );
    }
    
    displayFlights(filteredFlights);
}

// Reset filters
function resetFilters() {
    document.querySelectorAll('.airline-filter').forEach(cb => cb.checked = true);
    document.querySelectorAll('.time-filter').forEach(cb => cb.checked = false);
    document.getElementById('price-range').value = 20000;
    document.getElementById('price-value').textContent = '₹20,000';
    document.querySelector('input[name="sort"][value="price"]').checked = true;
    
    applyFilters();
}

// Show no results message
function showNoResults() {
    document.getElementById('flights-container').innerHTML = '';
    document.getElementById('no-results').style.display = 'block';
    document.getElementById('results-count').textContent = 'No flights found';
}

// Mobile menu
document.getElementById('hamburger').addEventListener('click', () => {
    document.querySelector('.nav-links').classList.toggle('active');
});
