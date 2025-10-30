# Suchitra Cosmetics - Django E-commerce Platform

Suchitra Cosmetics is a full-featured e-commerce web application built with Python and Django. It provides a clean, modern, and responsive interface for customers to browse and purchase cosmetic products, and a secure management area for administrators to manage the product inventory.

## Features

- **User Authentication**: Secure user registration, login, and logout functionality.
- **Product Catalog**:
    - Homepage with featured products and category navigation.
    - "Shop All Products" page with advanced filtering and sorting.
    - Dynamic category pages.
    - Detailed product pages with image galleries.
- **Shopping Cart**: Persistent session-based shopping cart to add and remove products.
- **Search**: Site-wide search functionality to find products by name, description, or category.
- **Advanced Filtering & Sorting**:
    - Filter products by category, brand, and price range.
    - Sort products by price, name, or newest arrivals.
- **Admin Product Management**: A separate, secure interface for superusers to add, update, and delete products and their images.
- **Custom Management Commands**: Scripts to import product data from CSV files.

## Tech Stack

- **Backend**: Python, Django
- **Frontend**: HTML, Tailwind CSS, Alpine.js
- **Database**: PostgreSQL (recommended for production)

---

## Local Development Setup

Follow these steps to get the project running on your local machine.

### 1. Prerequisites

- Python 3.10+
- Git
- PostgreSQL (or another database supported by Django)

### 2. Clone the Repository

```bash
git clone <your-repository-url>
cd suchitra_cosmatics
```

### 3. Set Up Virtual Environment

Create and activate a virtual environment to manage project dependencies.

```bash
# For macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# For Windows
python -m venv .venv
.venv\Scripts\activate
```

### 4. Install Dependencies

Install all required Python packages.

```bash
# First, ensure you have a requirements.txt file by running:
# pip freeze > requirements.txt

pip install -r requirements.txt
```

### 5. Configure Environment Variables

The project uses a `.env` file to manage sensitive information and environment-specific settings. Create a `.env` file in the project root directory (`suchitra_cosmatics/`) and add the following variables.

```env
# .env

# SECURITY WARNING: Generate a new secret key for your project!
SECRET_KEY='your-django-secret-key'

# Set to True for development, False for production
DEBUG=True

# Example for PostgreSQL. Update with your database credentials.
DATABASE_URL='postgres://USER:PASSWORD@HOST:PORT/NAME'

# Example for SQLite (simpler for initial setup)
# DATABASE_URL='sqlite:///db.sqlite3'
```

### 6. Apply Database Migrations

Run the following command to create the database tables based on the app models.

```bash
python manage.py migrate
```

### 7. Create a Superuser

A superuser account is required to access the Django admin (`/site-admin/`) and the product management interface (`/manage/products/`).

```bash
python manage.py createsuperuser
```
Follow the prompts to set a username, email, and password.

### 8. Import Initial Data (Optional)

You can populate the database with initial product data using the custom management command.

```bash
# Make sure your CSV file is in the specified path
python manage.py import_products /path/to/your/cosmetics.csv --image_dir /path/to/your/images
```

### 9. Run the Development Server

You're all set! Start the Django development server.

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`.

---

## Deployment

To deploy this application to a production environment (e.g., Heroku, Render, DigitalOcean), follow these general steps:

1.  **Environment Variables**:
    - Set `DEBUG=False` in your production environment.
    - Set `SECRET_KEY` to a secure, randomly generated value.
    - Configure `ALLOWED_HOSTS` with your domain name.
    - Ensure the `DATABASE_URL` points to your production database.

2.  **Static and Media Files**:
    - Configure a service like Amazon S3, Google Cloud Storage, or WhiteNoise to serve static and media files.
    - Run `python manage.py collectstatic` to gather all static files into a single directory.

3.  **Web Server**:
    - Use a production-ready WSGI server like **Gunicorn** or **uWSGI** to run the application.
    - Example Gunicorn command: `gunicorn suchitra_cosmatics.wsgi:application`

4.  **Reverse Proxy**:
    - Place a web server like **Nginx** or **Apache** in front of your WSGI server to handle incoming HTTP requests, serve static files, and manage SSL.

---

## Deployment with Docker

This project is configured for easy deployment using Docker and Docker Compose. This method encapsulates the application and its dependencies into containers for a consistent and portable environment.

### 1. Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 2. Configure Environment Variables

The `docker-compose.yml` file reads from a `.env` file. Make sure your `.env` file is correctly configured for production.

```env
# .env

# SECURITY WARNING: Use a strong, unique key for production!
SECRET_KEY='your-production-django-secret-key'

# Set to False for production
DEBUG=False

# Add your domain name and 'localhost' for health checks
ALLOWED_HOSTS=yourdomain.com,localhost,127.0.0.1

# PostgreSQL Database Credentials
# These must match the values in docker-compose.yml
POSTGRES_DB=suchitra_db
POSTGRES_USER=suchitra_user
POSTGRES_PASSWORD=your_strong_password

# Database URL for Django
DATABASE_URL='postgres://suchitra_user:your_strong_password@db:5432/suchitra_db'
```

**Note**: The `DATABASE_URL` host is `db`, which is the name of the database service defined in `docker-compose.yml`.

### 3. Build and Run the Containers

From the project root directory (where `docker-compose.yml` is located), run the following command to build the images and start the services in the background:

```bash
docker-compose up --build -d
```

- `--build`: Forces Docker to rebuild the image, picking up any changes in your code or `Dockerfile`.
- `-d`: Runs the containers in detached mode (in the background).

### 4. Initial Setup (First-Time Run)

The `entrypoint.sh` script will automatically run database migrations. However, you still need to create a superuser inside the running container.

```bash
# Create a superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files (if not handled in Dockerfile)
docker-compose exec web python manage.py collectstatic --no-input
```

Your application should now be running and accessible on port 8000 of your server.

### 5. Managing the Application

- **To stop the services**: `docker-compose down`
- **To view logs**: `docker-compose logs -f web`
- **To run a management command**: `docker-compose exec web python manage.py <command>`