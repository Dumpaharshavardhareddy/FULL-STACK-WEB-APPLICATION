# MovieBook - Movie Ticket Booking Platform

A comprehensive movie ticket booking platform built with HTML, CSS, JavaScript, Bootstrap for the frontend and Django with MySQL for the backend.

## Features

### User Features
- **User Registration & Login** - Secure authentication with validation
- **Movie Browsing** - Filter by location, genre, language
- **Theater & Showtime Selection** - View available theaters and showtimes
- **Dynamic Seat Selection** - Interactive seat map with real-time availability
- **Booking Cart & Summary** - Review booking details before payment
- **Payment Integration** - Mock payment gateway (can be integrated with Razorpay/Stripe)
- **Booking Confirmation** - Digital ticket generation
- **User Profile** - View booking history and manage preferences
- **Mobile Responsive** - Optimized for all devices

### Admin Features
- **Admin Dashboard** - Comprehensive admin panel
- **Movie Management** - Add, edit, delete movies
- **Theater Management** - Manage theaters, screens, and showtimes
- **Booking Management** - View and manage all bookings
- **User Management** - Manage user accounts
- **Analytics** - Booking statistics and revenue reports

## Technology Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with custom properties
- **JavaScript (ES6+)** - Interactive functionality
- **Bootstrap 5** - Responsive framework
- **Font Awesome** - Icons

### Backend
- **Django 4.2** - Python web framework
- **Django REST Framework** - API development
- **MySQL** - Database
- **Python 3.8+** - Programming language

## Project Structure

```
moviebook-platform/
├── frontend/
│   ├── index.html          # Main HTML file
│   ├── style.css           # Custom styles
│   ├── main.js            # JavaScript functionality
│   └── assets/            # Images and other assets
├── backend/
│   ├── moviebook/         # Django project settings
│   ├── users/             # User management app
│   ├── movies/            # Movie management app
│   ├── theaters/          # Theater and show management app
│   ├── bookings/          # Booking and payment app
│   ├── manage.py          # Django management script
│   └── requirements.txt   # Python dependencies
└── README.md
```

## Database Schema

### Key Models
- **User** - Custom user model with profile information
- **Movie** - Movie details with genres and languages
- **Theater** - Theater information with location
- **Screen** - Individual screens within theaters
- **Show** - Movie showtimes
- **Booking** - Ticket bookings
- **Payment** - Payment transactions
- **Seat** - Individual seats with categories

## Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL 5.7+
- Node.js (for development server)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd moviebook-platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Database setup**
   ```bash
   # Create MySQL database
   mysql -u root -p
   CREATE DATABASE moviebook_db;
   exit
   ```

5. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Load sample data (optional)**
   ```bash
   python manage.py loaddata fixtures/sample_data.json
   ```

9. **Start development server**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout

### Movies
- `GET /api/movies/` - List movies
- `GET /api/movies/<slug>/` - Movie details
- `GET /api/movies/featured/` - Featured movies
- `GET /api/movies/search/` - Search movies

### Theaters
- `GET /api/theaters/` - List theaters
- `GET /api/theaters/<id>/` - Theater details
- `GET /api/theaters/shows/` - List shows
- `GET /api/theaters/shows/<id>/seats/` - Seat layout

### Bookings
- `POST /api/bookings/create/` - Create booking
- `GET /api/bookings/` - User bookings
- `GET /api/bookings/<booking_id>/` - Booking details
- `POST /api/bookings/payments/create/` - Create payment

## Features Implementation

### User Authentication
- Custom user model with extended profile
- Token-based authentication
- Email validation and verification
- Password strength validation

### Movie Management
- Rich movie information with posters
- Genre and language categorization
- Rating and review system
- Search and filtering capabilities

### Theater & Show Management
- Multi-screen theater support
- Flexible seat categorization
- Dynamic pricing per show
- Real-time seat availability

### Booking System
- Interactive seat selection
- Booking expiry mechanism
- Payment integration ready
- Booking confirmation and tickets

### Admin Panel
- Comprehensive Django admin
- Custom admin views for analytics
- Bulk operations support
- User and booking management

## Security Features

- CSRF protection
- SQL injection prevention
- XSS protection
- Secure password hashing
- Token-based authentication
- Input validation and sanitization

## Performance Optimizations

- Database query optimization
- Efficient seat availability checking
- Caching for frequently accessed data
- Optimized API responses
- Responsive image loading

## Deployment

### Production Setup
1. Set `DEBUG=False` in settings
2. Configure production database
3. Set up static file serving
4. Configure email backend
5. Set up SSL certificates
6. Configure payment gateways

### Environment Variables
```bash
SECRET_KEY=your-production-secret-key
DEBUG=False
DB_NAME=moviebook_production
DB_USER=production_user
DB_PASSWORD=secure_password
DB_HOST=your-db-host
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Email: support@moviebook.com

## Roadmap

- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Social media integration
- [ ] Loyalty program
- [ ] Push notifications
- [ ] Advanced search filters
- [ ] Recommendation engine