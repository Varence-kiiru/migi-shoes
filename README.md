# Migi Shoes Website

A full-featured e-commerce website for footwear shopping, built with Django. This project provides a complete online store experience with user authentication, product management, shopping cart functionality, and an admin dashboard.

## Features

- **User Authentication**: Registration, login, password reset functionality
- **Product Management**: Browse shoes by brand, gender, and category
- **Shopping Cart**: Add/remove items, update quantities
- **Checkout Process**: Secure order placement with payment methods
- **Customer Dashboard**: Order history, profile management, addresses, payment methods
- **Admin Panel**: Comprehensive dashboard for inventory management, order processing, and analytics
- **Search & Filtering**: Find products by various criteria
- **Wishlist**: Save favorite items for later
- **Responsive Design**: Mobile-friendly interface

## Tech Stack

- **Backend**: Django 4.x
- **Database**: SQLite (configurable)
- **Frontend**: HTML5, CSS3, JavaScript
- **Email**: SMTP integration
- **Deployment**: Ready for production with WSGI/ASGI support

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Varence-kiiru/migi-shoes.git
   cd migi-shoes
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your actual configuration values.

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Load sample data (optional)**
   ```bash
   python manage.py loaddata fixtures/core/users.json
   python manage.py loaddata fixtures/products/brands.json
   python manage.py loaddata fixtures/products/shoes.json
   # Add other fixtures as needed
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

   Visit `http://127.0.0.1:8000` in your browser.

## Configuration

Key settings in `.env`:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to `False` in production
- `DATABASE_NAME`: Database file path
- `EMAIL_HOST`: SMTP server for email functionality
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

## Usage

- **Storefront**: Browse and purchase shoes
- **Admin**: Access `/admin/` for Django admin or `/admin-panel/` for custom dashboard
- **API**: RESTful endpoints available (documented in views)

## Project Structure

```
migi-shoes/
├── accounts/          # User authentication
├── admin_panel/       # Custom admin dashboard
├── cart/              # Shopping cart functionality
├── customer/          # Customer profiles and orders
├── products/          # Product models and views
├── storefront/        # Main store pages
├── BaseTemplate/      # Base templates and static files
├── Core/              # Core models
├── models_app/        # Shared models
├── Migi_shoes/        # Django project settings
├── media/             # User-uploaded files
├── static/            # Static assets
└── fixtures/          # Sample data
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please open an issue on GitHub.
