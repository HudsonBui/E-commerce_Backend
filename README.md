Collecting workspace information# E-commerce Backend

A robust and scalable e-commerce REST API backend built with Django and Django REST Framework. This project provides comprehensive endpoints for managing users, products, categories, cart functionality, orders, and authentication.

## Features

- **User Management**
  - Registration with email verification
  - Authentication with token-based system
  - Social authentication (Google, Facebook)
  - Profile management with image upload

- **Product System**
  - Categorization with hierarchical structure
  - Product variants (color, size)
  - Detailed product information
  - Image management
  - Pricing and stock control

- **Order Processing**
  - Shopping cart functionality
  - Order placement and history
  - Order status tracking

- **API Documentation**
  - Automatic OpenAPI schema generation
  - Interactive API documentation

## Tech Stack

- **Framework**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: Token-based auth, Social auth (OAuth2)
- **Documentation**: drf-spectacular (OpenAPI)
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/E-commerce_Backend.git
   cd E-commerce_Backend
   ```

2. Create a .env file in the project root with the following variables:
   ```
   POSTGRES_DB=ecommerce
   POSTGRES_USER=your_user
   POSTGRES_PASSWORD=your_password
   SECRET_DOCKER_SETTINGS_KEY=your_secret_key

   # Optional social auth credentials
   GOOGLE_OAUTH2_KEY=your_google_key
   GOOGLE_OAUTH2_SECRET=your_google_secret
   FACEBOOK_KEY=your_facebook_key
   FACEBOOK_SECRET=your_facebook_secret
   ```

### Running the Application

1. Start the containers:
   ```bash
   docker-compose up
   ```

2. Access the API at http://127.0.0.1:8000/api/
3. API Documentation is available at http://127.0.0.1:8000/api/docs/



### Products

- `GET /api/product/products/generic/`: List all products with basic information
- `GET /api/product/products/generic/{id}/`: Get detailed product information
- Supports filtering by category and name

## Development

### Running Tests

```bash
docker-compose run --rm app sh -c "python manage.py test"
```

### Code Quality

```bash
docker-compose run --rm app sh -c "flake8"
```

### Making Migrations

```bash
docker-compose run --rm app sh -c "python manage.py makemigrations"
docker-compose run --rm app sh -c "python manage.py migrate"
```

### Creating a Superuser

```bash
docker-compose run --rm app sh -c "python manage.py createsuperuser"
```

## Deployment

The application is containerized and ready for deployment to various platforms:

- For production deployment, update the settings.py file to:
  - Set `DEBUG=False`
  - Configure proper email backend settings
  - Add your domain to `ALLOWED_HOSTS`
  - Set up proper static and media file serving

## Project Structure

```
app/
  ├── app/ - Project settings and main URLs
  ├── core/ - Core models and utilities
  ├── user/ - User management and authentication
  ├── email_verification/ - Email verification system
  ├── oauth/ - Social authentication
  ├── product/ - Product management and catalog
```

## License

[Your License Here]

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

*Note: This README will be updated with more information as the project evolves.*

Similar code found with 1 license type