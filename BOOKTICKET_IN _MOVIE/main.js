// Global variables
let currentUser = null;
let selectedMovie = null;
let selectedTheater = null;
let selectedShowtime = null;
let selectedSeats = [];
let totalAmount = 0;
let currentLocation = 'Mumbai';
let currentBooking = null;
let userBookings = [];

// Sample data (In real app, this would come from Django backend)
const sampleMovies = [
    {
        id: 1,
        title: "Avengers: Endgame",
        genre: "Action, Adventure",
        rating: 4.5,
        languages: ["English", "Hindi"],
        poster: "https://images.pexels.com/photos/7991579/pexels-photo-7991579.jpeg?auto=compress&cs=tinysrgb&w=400",
        description: "After the devastating events of Avengers: Infinity War, the universe is in ruins.",
        duration: "181 min",
        releaseDate: "2024-01-15"
    },
    {
        id: 2,
        title: "The Dark Knight",
        genre: "Action, Crime, Drama",
        rating: 4.8,
        languages: ["English"],
        poster: "https://images.pexels.com/photos/7991579/pexels-photo-7991579.jpeg?auto=compress&cs=tinysrgb&w=400",
        description: "Batman faces his greatest challenge yet with the Joker terrorizing Gotham City.",
        duration: "152 min",
        releaseDate: "2024-01-20"
    },
    {
        id: 3,
        title: "Dangal",
        genre: "Biography, Drama, Sport",
        rating: 4.6,
        languages: ["Hindi"],
        poster: "https://images.pexels.com/photos/7991579/pexels-photo-7991579.jpeg?auto=compress&cs=tinysrgb&w=400",
        description: "A former wrestler trains his daughters to become world-class wrestlers.",
        duration: "161 min",
        releaseDate: "2024-01-25"
    },
    {
        id: 4,
        title: "Spider-Man: No Way Home",
        genre: "Action, Adventure, Fantasy",
        rating: 4.7,
        languages: ["English", "Hindi"],
        poster: "https://images.pexels.com/photos/7991579/pexels-photo-7991579.jpeg?auto=compress&cs=tinysrgb&w=400",
        description: "Spider-Man's identity is revealed and he seeks help from Doctor Strange.",
        duration: "148 min",
        releaseDate: "2024-02-01"
    }
];

const sampleTheaters = [
    {
        id: 1,
        name: "PVR Cinemas",
        location: "Phoenix Mall, Mumbai",
        facilities: ["Dolby Atmos", "IMAX", "Recliner"],
        image: "https://images.pexels.com/photos/7991579/pexels-photo-7991579.jpeg?auto=compress&cs=tinysrgb&w=400"
    },
    {
        id: 2,
        name: "INOX Multiplex",
        location: "R City Mall, Mumbai",
        facilities: ["4DX", "Screen X", "Premium"],
        image: "https://images.pexels.com/photos/7991579/pexels-photo-7991579.jpeg?auto=compress&cs=tinysrgb&w=400"
    },
    {
        id: 3,
        name: "Cinepolis",
        location: "Palladium Mall, Mumbai",
        facilities: ["VIP", "IMAX", "Gourmet"],
        image: "https://images.pexels.com/photos/7991579/pexels-photo-7991579.jpeg?auto=compress&cs=tinysrgb&w=400"
    }
];

const showtimes = {
    1: [
        { theater: "PVR Cinemas", times: ["10:00 AM", "1:30 PM", "5:00 PM", "8:30 PM"], price: 250 },
        { theater: "INOX Multiplex", times: ["11:00 AM", "2:30 PM", "6:00 PM", "9:30 PM"], price: 300 },
        { theater: "Cinepolis", times: ["12:00 PM", "3:30 PM", "7:00 PM", "10:30 PM"], price: 350 }
    ]
};

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    loadMovies();
    loadTheaters();
    setupEventListeners();
    checkAuthStatus();
    loadUserBookings();
});

// Setup event listeners
function setupEventListeners() {
    // Login form
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    
    // Register form
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    
    // Payment form
    document.getElementById('paymentForm').addEventListener('submit', handlePayment);
    
    // Search functionality
    document.getElementById('searchInput').addEventListener('input', handleSearch);
    
    // Payment method toggle
    document.querySelectorAll('input[name="paymentMethod"]').forEach(radio => {
        radio.addEventListener('change', togglePaymentMethod);
    });
}

// Load movies from API (mock data for now)
function loadMovies() {
    const container = document.getElementById('moviesContainer');
    container.innerHTML = '<div class="loading"></div>';
    
    setTimeout(() => {
        container.innerHTML = '';
        sampleMovies.forEach(movie => {
            container.innerHTML += createMovieCard(movie);
        });
    }, 500);
}

// Create movie card HTML
function createMovieCard(movie) {
    const stars = '★'.repeat(Math.floor(movie.rating)) + '☆'.repeat(5 - Math.floor(movie.rating));
    const languageBadges = movie.languages.map(lang => 
        `<span class="language-badge">${lang}</span>`
    ).join('');
    
    return `
        <div class="col-lg-3 col-md-4 col-sm-6 mb-4">
            <div class="movie-card">
                <img src="${movie.poster}" alt="${movie.title}" class="movie-poster">
                <div class="movie-info">
                    <h5 class="movie-title">${movie.title}</h5>
                    <p class="movie-genre">${movie.genre}</p>
                    <div class="movie-rating">
                        <span class="rating-stars">${stars}</span>
                        <span>${movie.rating}/5</span>
                    </div>
                    <div class="movie-languages">
                        ${languageBadges}
                    </div>
                    <button class="btn btn-primary w-100" onclick="selectMovie(${movie.id})">
                        Book Tickets
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Load theaters
function loadTheaters() {
    const container = document.getElementById('theatersContainer');
    container.innerHTML = '<div class="loading"></div>';
    
    setTimeout(() => {
        container.innerHTML = '';
        sampleTheaters.forEach(theater => {
            container.innerHTML += createTheaterCard(theater);
        });
    }, 500);
}

// Create theater card HTML
function createTheaterCard(theater) {
    const facilityBadges = theater.facilities.map(facility => 
        `<span class="facility-badge">${facility}</span>`
    ).join('');
    
    return `
        <div class="col-lg-4 col-md-6 mb-4">
            <div class="theater-card">
                <h5 class="theater-name">${theater.name}</h5>
                <p class="theater-location"><i class="fas fa-map-marker-alt me-1"></i>${theater.location}</p>
                <div class="theater-facilities">
                    ${facilityBadges}
                </div>
                <button class="btn btn-outline-primary" onclick="viewTheaterDetails(${theater.id})">
                    View Details
                </button>
            </div>
        </div>
    `;
}

// Movie selection
function selectMovie(movieId) {
    selectedMovie = sampleMovies.find(m => m.id === movieId);
    if (!selectedMovie) return;
    
    showMovieDetails();
}

// Show movie details modal
function showMovieDetails() {
    const modal = new bootstrap.Modal(document.getElementById('movieModal'));
    const modalTitle = document.getElementById('movieModalTitle');
    const modalBody = document.getElementById('movieModalBody');
    
    modalTitle.textContent = selectedMovie.title;
    modalBody.innerHTML = `
        <div class="row">
            <div class="col-md-4">
                <img src="${selectedMovie.poster}" alt="${selectedMovie.title}" class="img-fluid rounded">
            </div>
            <div class="col-md-8">
                <h5>${selectedMovie.title}</h5>
                <p><strong>Genre:</strong> ${selectedMovie.genre}</p>
                <p><strong>Duration:</strong> ${selectedMovie.duration}</p>
                <p><strong>Rating:</strong> ${selectedMovie.rating}/5</p>
                <p><strong>Languages:</strong> ${selectedMovie.languages.join(', ')}</p>
                <p><strong>Release Date:</strong> ${selectedMovie.releaseDate}</p>
                <p><strong>Description:</strong> ${selectedMovie.description}</p>
                <button class="btn btn-primary" onclick="selectTheater()">
                    <i class="fas fa-calendar-alt me-2"></i>Select Showtime
                </button>
            </div>
        </div>
    `;
    
    modal.show();
}

// Select theater and showtime
function selectTheater() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('movieModal'));
    modal.hide();
    
    const theaterModal = new bootstrap.Modal(document.getElementById('theaterModal'));
    const modalBody = document.getElementById('theaterModalBody');
    
    const movieShowtimes = showtimes[selectedMovie.id] || [];
    
    modalBody.innerHTML = `
        <div class="mb-3">
            <h6>${selectedMovie.title}</h6>
            <p class="text-muted">${selectedMovie.genre} • ${selectedMovie.duration}</p>
        </div>
        ${movieShowtimes.map(show => `
            <div class="showtime-card">
                <div class="theater-info">
                    <div>
                        <div class="theater-name-show">${show.theater}</div>
                        <div class="text-muted">₹${show.price} per ticket</div>
                    </div>
                    <div class="theater-facilities-show">
                        <span class="facility-badge">Dolby Atmos</span>
                        <span class="facility-badge">Recliner</span>
                    </div>
                </div>
                <div class="showtimes">
                    ${show.times.map(time => `
                        <button class="showtime-btn" onclick="selectShowtime('${show.theater}', '${time}', ${show.price})">
                            ${time}
                        </button>
                    `).join('')}
                </div>
            </div>
        `).join('')}
    `;
    
    theaterModal.show();
}

// Select specific showtime
function selectShowtime(theater, time, price) {
    selectedTheater = theater;
    selectedShowtime = time;
    
    // Remove previous selections
    document.querySelectorAll('.showtime-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // Mark current selection
    event.target.classList.add('selected');
    
    setTimeout(() => {
        const theaterModal = bootstrap.Modal.getInstance(document.getElementById('theaterModal'));
        theaterModal.hide();
        showSeatSelection(price);
    }, 500);
}

// Show seat selection
function showSeatSelection(ticketPrice) {
    const modal = new bootstrap.Modal(document.getElementById('seatModal'));
    const modalBody = document.getElementById('seatModalBody');
    
    modalBody.innerHTML = `
        <div class="seat-map">
            <div class="screen">SCREEN</div>
            ${generateSeatMap(ticketPrice)}
            <div class="seat-legend">
                <div class="legend-item">
                    <div class="legend-seat legend-available"></div>
                    <span>Available</span>
                </div>
                <div class="legend-item">
                    <div class="legend-seat legend-selected"></div>
                    <span>Selected</span>
                </div>
                <div class="legend-item">
                    <div class="legend-seat legend-occupied"></div>
                    <span>Occupied</span>
                </div>
            </div>
        </div>
    `;
    
    modal.show();
    window.ticketPrice = ticketPrice;
}

// Generate seat map
function generateSeatMap(ticketPrice) {
    const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
    const seatsPerRow = 12;
    let seatMap = '';
    
    // Some randomly occupied seats for demo
    const occupiedSeats = ['A3', 'A4', 'B7', 'C2', 'D5', 'E8', 'F1', 'G6'];
    
    rows.forEach(row => {
        seatMap += '<div class="seat-row">';
        seatMap += `<div class="row-label">${row}</div>`;
        
        for (let i = 1; i <= seatsPerRow; i++) {
            const seatId = row + i;
            const isOccupied = occupiedSeats.includes(seatId);
            const seatClass = isOccupied ? 'seat occupied' : 'seat';
            
            seatMap += `<div class="${seatClass}" data-seat="${seatId}" onclick="toggleSeat('${seatId}', ${ticketPrice})">${i}</div>`;
        }
        
        seatMap += '</div>';
    });
    
    return seatMap;
}

// Toggle seat selection
function toggleSeat(seatId, ticketPrice) {
    const seatElement = document.querySelector(`[data-seat="${seatId}"]`);
    
    if (seatElement.classList.contains('occupied')) {
        return;
    }
    
    if (seatElement.classList.contains('selected')) {
        seatElement.classList.remove('selected');
        selectedSeats = selectedSeats.filter(seat => seat !== seatId);
    } else {
        if (selectedSeats.length >= 10) {
            alert('You can select maximum 10 seats');
            return;
        }
        seatElement.classList.add('selected');
        selectedSeats.push(seatId);
    }
    
    updateSeatSummary(ticketPrice);
}

// Update seat summary
function updateSeatSummary(ticketPrice) {
    const selectedSeatsElement = document.getElementById('selectedSeats');
    const totalAmountElement = document.getElementById('totalAmount');
    const proceedBtn = document.getElementById('proceedBtn');
    
    if (selectedSeats.length > 0) {
        selectedSeatsElement.textContent = selectedSeats.join(', ');
        totalAmount = selectedSeats.length * ticketPrice;
        totalAmountElement.textContent = totalAmount;
        proceedBtn.disabled = false;
    } else {
        selectedSeatsElement.textContent = 'None';
        totalAmount = 0;
        totalAmountElement.textContent = '0';
        proceedBtn.disabled = true;
    }
}

// Proceed to payment
function proceedToPayment() {
    if (selectedSeats.length === 0) {
        alert('Please select at least one seat');
        return;
    }
    
    const seatModal = bootstrap.Modal.getInstance(document.getElementById('seatModal'));
    seatModal.hide();
    
    showPaymentModal();
}

// Show payment modal
function showPaymentModal() {
    const modal = new bootstrap.Modal(document.getElementById('paymentModal'));
    const summaryElement = document.getElementById('bookingSummary');
    
    const convenienceFee = selectedSeats.length * 20;
    const finalAmount = totalAmount + convenienceFee;
    
    summaryElement.innerHTML = `
        <div class="summary-row">
            <span><strong>Movie:</strong></span>
            <span>${selectedMovie.title}</span>
        </div>
        <div class="summary-row">
            <span><strong>Theater:</strong></span>
            <span>${selectedTheater}</span>
        </div>
        <div class="summary-row">
            <span><strong>Showtime:</strong></span>
            <span>${selectedShowtime}</span>
        </div>
        <div class="summary-row">
            <span><strong>Seats:</strong></span>
            <span>${selectedSeats.join(', ')}</span>
        </div>
        <div class="summary-row">
            <span><strong>Tickets:</strong></span>
            <span>${selectedSeats.length} × ₹${window.ticketPrice}</span>
        </div>
        <div class="summary-row">
            <span><strong>Convenience Fee:</strong></span>
            <span>₹${convenienceFee}</span>
        </div>
        <div class="summary-row summary-total">
            <span><strong>Total Amount:</strong></span>
            <span><strong>₹${finalAmount}</strong></span>
        </div>
    `;
    
    modal.show();
}

// Toggle payment method
function togglePaymentMethod() {
    const cardDetails = document.getElementById('cardDetails');
    const upiDetails = document.getElementById('upiDetails');
    const selectedMethod = document.querySelector('input[name="paymentMethod"]:checked').value;
    
    if (selectedMethod === 'credit') {
        cardDetails.classList.remove('d-none');
        upiDetails.classList.add('d-none');
    } else {
        cardDetails.classList.add('d-none');
        upiDetails.classList.remove('d-none');
    }
}

// Handle payment
function handlePayment(event) {
    event.preventDefault();
    
    // Mock payment processing
    const paymentModal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
    paymentModal.hide();
    
    // Create booking object
    const convenienceFee = selectedSeats.length * 20;
    const finalAmount = totalAmount + convenienceFee;
    const bookingId = generateBookingId();
    
    currentBooking = {
        id: bookingId,
        movie: selectedMovie,
        theater: selectedTheater,
        showtime: selectedShowtime,
        seats: [...selectedSeats],
        ticketPrice: window.ticketPrice,
        convenienceFee: convenienceFee,
        totalAmount: finalAmount,
        bookingDate: new Date().toISOString(),
        status: 'confirmed',
        paymentMethod: document.querySelector('input[name="paymentMethod"]:checked').value
    };
    
    // Add to user bookings
    if (currentUser) {
        userBookings.unshift(currentBooking);
        localStorage.setItem(`bookings_${currentUser.email}`, JSON.stringify(userBookings));
    }
    
    // Show success modal
    setTimeout(() => {
        showBookingSuccess();
        sendEmailConfirmation();
    }, 1000);
}

// Generate booking ID
function generateBookingId() {
    return 'MB' + Date.now().toString().slice(-8) + Math.random().toString(36).substr(2, 4).toUpperCase();
}

// Show booking success modal
function showBookingSuccess() {
    const modal = new bootstrap.Modal(document.getElementById('bookingSuccessModal'));
    const ticketDetails = document.getElementById('ticketDetails');
    
    const showDate = new Date();
    showDate.setDate(showDate.getDate() + 1); // Tomorrow's show
    
    ticketDetails.innerHTML = `
        <div class="ticket-container">
            <div class="ticket-header">
                <div class="row">
                    <div class="col-md-8">
                        <h4 class="mb-1">${currentBooking.movie.title}</h4>
                        <p class="text-muted mb-0">${currentBooking.movie.genre}</p>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="qr-code">
                            <i class="fas fa-qrcode" style="font-size: 3rem; color: #6c757d;"></i>
                            <small class="d-block text-muted">Scan at theater</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="ticket-body">
                <div class="row">
                    <div class="col-md-6">
                        <div class="ticket-info">
                            <div class="info-item">
                                <span class="label">Booking ID:</span>
                                <span class="value">${currentBooking.id}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">Theater:</span>
                                <span class="value">${currentBooking.theater}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">Show Date:</span>
                                <span class="value">${showDate.toDateString()}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">Show Time:</span>
                                <span class="value">${currentBooking.showtime}</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="ticket-info">
                            <div class="info-item">
                                <span class="label">Seats:</span>
                                <span class="value">${currentBooking.seats.join(', ')}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">Tickets:</span>
                                <span class="value">${currentBooking.seats.length} × ₹${currentBooking.ticketPrice}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">Convenience Fee:</span>
                                <span class="value">₹${currentBooking.convenienceFee}</span>
                            </div>
                            <div class="info-item total">
                                <span class="label">Total Paid:</span>
                                <span class="value">₹${currentBooking.totalAmount}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="ticket-footer">
                <div class="row">
                    <div class="col-md-6">
                        <small class="text-muted">
                            <i class="fas fa-info-circle me-1"></i>
                            Please arrive 30 minutes before showtime
                        </small>
                    </div>
                    <div class="col-md-6 text-end">
                        <small class="text-muted">
                            Booked on ${new Date().toLocaleString()}
                        </small>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    modal.show();
    resetBookingFlow();
}

// Send email confirmation (mock)
function sendEmailConfirmation() {
    if (currentUser && currentUser.email) {
        console.log(`Email confirmation sent to ${currentUser.email}`);
        // In real implementation, this would call the backend API
        // to send an actual email with ticket details
    }
}

// Download ticket
function downloadTicket() {
    // Mock download functionality
    alert('Ticket download started! Check your downloads folder.');
    // In real implementation, this would generate a PDF ticket
}

// Share ticket
function shareTicket() {
    if (navigator.share) {
        navigator.share({
            title: 'Movie Ticket',
            text: `I just booked tickets for ${currentBooking.movie.title}!`,
            url: window.location.href
        });
    } else {
        // Fallback for browsers that don't support Web Share API
        const shareText = `I just booked tickets for ${currentBooking.movie.title} at ${currentBooking.theater}!`;
        navigator.clipboard.writeText(shareText).then(() => {
            alert('Ticket details copied to clipboard!');
        });
    }
}

// View bookings
function viewBookings() {
    const successModal = bootstrap.Modal.getInstance(document.getElementById('bookingSuccessModal'));
    successModal.hide();
    
    setTimeout(() => {
        showBookings();
    }, 300);
}

// Reset booking flow
function resetBookingFlow() {
    selectedMovie = null;
    selectedTheater = null;
    selectedShowtime = null;
    selectedSeats = [];
    totalAmount = 0;
    currentBooking = null;
}

// Handle login
function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    // Mock authentication
    if (email && password) {
        currentUser = {
            name: 'John Doe',
            email: email
        };
        
        updateUserInterface();
        loadUserBookings();
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
        modal.hide();
        
        alert('Login successful!');
    }
}

// Handle registration
function handleRegister(event) {
    event.preventDefault();
    
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    if (password !== confirmPassword) {
        alert('Passwords do not match');
        return;
    }
    
    // Mock registration
    currentUser = {
        name: name,
        email: email
    };
    
    updateUserInterface();
    loadUserBookings();
    
    const modal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
    modal.hide();
    
    alert('Registration successful!');
}

// Update user interface after login
function updateUserInterface() {
    const userActions = document.querySelector('.user-actions');
    const userMenu = document.querySelector('.user-menu');
    const userName = document.getElementById('userName');
    
    if (currentUser) {
        userActions.children[0].classList.add('d-none'); // Sign In button
        userActions.children[1].classList.add('d-none'); // Sign Up button
        userMenu.classList.remove('d-none');
        userName.textContent = currentUser.name;
        
        // Store user data
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
    }
}

// Check authentication status
function checkAuthStatus() {
    // Check if user is logged in (localStorage in real app)
    const userData = localStorage.getItem('currentUser');
    if (userData) {
        currentUser = JSON.parse(userData);
        updateUserInterface();
    }
}

// Load user bookings
function loadUserBookings() {
    if (currentUser) {
        const savedBookings = localStorage.getItem(`bookings_${currentUser.email}`);
        if (savedBookings) {
            userBookings = JSON.parse(savedBookings);
        }
    }
}

// Show login modal
function showLogin() {
    const registerModal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
    if (registerModal) registerModal.hide();
    
    const modal = new bootstrap.Modal(document.getElementById('loginModal'));
    modal.show();
}

// Show register modal
function showRegister() {
    const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
    if (loginModal) loginModal.hide();
    
    const modal = new bootstrap.Modal(document.getElementById('registerModal'));
    modal.show();
}

// Show bookings
function showBookings() {
    if (!currentUser) {
        showLogin();
        return;
    }
    
    const modal = new bootstrap.Modal(document.getElementById('bookingHistoryModal'));
    const bookingsList = document.getElementById('bookingHistoryList');
    
    if (userBookings.length === 0) {
        bookingsList.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-ticket-alt text-muted" style="font-size: 3rem;"></i>
                <h5 class="mt-3 text-muted">No bookings found</h5>
                <p class="text-muted">Start booking your favorite movies!</p>
                <button class="btn btn-primary" onclick="closeBookingHistory()">
                    <i class="fas fa-film me-2"></i>Browse Movies
                </button>
            </div>
        `;
    } else {
        bookingsList.innerHTML = userBookings.map(booking => createBookingCard(booking)).join('');
    }
    
    modal.show();
}

// Create booking card
function createBookingCard(booking) {
    const bookingDate = new Date(booking.bookingDate);
    const statusClass = booking.status === 'confirmed' ? 'success' : 
                       booking.status === 'cancelled' ? 'danger' : 'warning';
    
    return `
        <div class="booking-card mb-3">
            <div class="card">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <img src="${booking.movie.poster}" alt="${booking.movie.title}" class="booking-poster">
                        </div>
                        <div class="col-md-6">
                            <h5 class="card-title">${booking.movie.title}</h5>
                            <p class="card-text">
                                <i class="fas fa-map-marker-alt me-2"></i>${booking.theater}<br>
                                <i class="fas fa-calendar me-2"></i>${bookingDate.toDateString()}<br>
                                <i class="fas fa-clock me-2"></i>${booking.showtime}<br>
                                <i class="fas fa-chair me-2"></i>Seats: ${booking.seats.join(', ')}
                            </p>
                        </div>
                        <div class="col-md-3 text-end">
                            <span class="badge bg-${statusClass} mb-2">${booking.status.toUpperCase()}</span>
                            <h5 class="text-primary">₹${booking.totalAmount}</h5>
                            <small class="text-muted">Booking ID: ${booking.id}</small>
                            <div class="mt-2">
                                <button class="btn btn-sm btn-outline-primary" onclick="viewTicketDetails('${booking.id}')">
                                    <i class="fas fa-eye me-1"></i>View
                                </button>
                                ${booking.status === 'confirmed' ? 
                                    `<button class="btn btn-sm btn-outline-danger ms-1" onclick="cancelBooking('${booking.id}')">
                                        <i class="fas fa-times me-1"></i>Cancel
                                    </button>` : ''
                                }
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// View ticket details
function viewTicketDetails(bookingId) {
    const booking = userBookings.find(b => b.id === bookingId);
    if (!booking) return;
    
    currentBooking = booking;
    
    const historyModal = bootstrap.Modal.getInstance(document.getElementById('bookingHistoryModal'));
    historyModal.hide();
    
    setTimeout(() => {
        showBookingSuccess();
    }, 300);
}

// Cancel booking
function cancelBooking(bookingId) {
    if (confirm('Are you sure you want to cancel this booking?')) {
        const bookingIndex = userBookings.findIndex(b => b.id === bookingId);
        if (bookingIndex !== -1) {
            userBookings[bookingIndex].status = 'cancelled';
            localStorage.setItem(`bookings_${currentUser.email}`, JSON.stringify(userBookings));
            showBookings(); // Refresh the list
            alert('Booking cancelled successfully!');
        }
    }
}

// Filter bookings
function filterBookings() {
    const status = document.getElementById('statusFilter').value;
    const date = document.getElementById('dateFilter').value;
    
    let filteredBookings = [...userBookings];
    
    if (status) {
        filteredBookings = filteredBookings.filter(booking => booking.status === status);
    }
    
    if (date) {
        filteredBookings = filteredBookings.filter(booking => {
            const bookingDate = new Date(booking.bookingDate).toISOString().split('T')[0];
            return bookingDate === date;
        });
    }
    
    const bookingsList = document.getElementById('bookingHistoryList');
    if (filteredBookings.length === 0) {
        bookingsList.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-search text-muted" style="font-size: 3rem;"></i>
                <h5 class="mt-3 text-muted">No bookings found</h5>
                <p class="text-muted">Try adjusting your filters</p>
            </div>
        `;
    } else {
        bookingsList.innerHTML = filteredBookings.map(booking => createBookingCard(booking)).join('');
    }
}

// Close booking history modal
function closeBookingHistory() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('bookingHistoryModal'));
    modal.hide();
}

// Logout
function logout() {
    currentUser = null;
    userBookings = [];
    localStorage.removeItem('currentUser');
    
    const userActions = document.querySelector('.user-actions');
    const userMenu = document.querySelector('.user-menu');
    
    userActions.children[0].classList.remove('d-none'); // Sign In button
    userActions.children[1].classList.remove('d-none'); // Sign Up button
    userMenu.classList.add('d-none');
    
    alert('Logged out successfully!');
}

// Change location
function changeLocation(location) {
    currentLocation = location;
    document.querySelector('.nav-link.dropdown-toggle').innerHTML = 
        `<i class="fas fa-map-marker-alt me-1"></i>${location}`;
    loadMovies();
    loadTheaters();
}

// Apply filters
function applyFilters() {
    const genre = document.getElementById('genreFilter').value;
    const language = document.getElementById('languageFilter').value;
    
    // Filter logic would go here
    console.log('Applying filters:', { genre, language });
    loadMovies(); // Reload with filters
}

// Handle search
function handleSearch(event) {
    const query = event.target.value.toLowerCase();
    
    if (query.length === 0) {
        loadMovies();
        return;
    }
    
    const filteredMovies = sampleMovies.filter(movie => 
        movie.title.toLowerCase().includes(query) ||
        movie.genre.toLowerCase().includes(query)
    );
    
    const container = document.getElementById('moviesContainer');
    container.innerHTML = '';
    
    if (filteredMovies.length === 0) {
        container.innerHTML = '<div class="col-12 text-center"><p>No movies found matching your search.</p></div>';
    } else {
        filteredMovies.forEach(movie => {
            container.innerHTML += createMovieCard(movie);
        });
    }
}

// View theater details
function viewTheaterDetails(theaterId) {
    const theater = sampleTheaters.find(t => t.id === theaterId);
    if (!theater) return;
    
    alert(`Theater: ${theater.name}\nLocation: ${theater.location}\nFacilities: ${theater.facilities.join(', ')}`);
}

// Show profile
function showProfile() {
    if (!currentUser) {
        showLogin();
        return;
    }
    
    alert(`Profile: ${currentUser.name}\nEmail: ${currentUser.email}\nTotal Bookings: ${userBookings.length}`);
}