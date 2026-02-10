# E-Commerce Product Catalog API

A REST API for an e-commerce product catalog - handles products, categories, user authentication with role-based access, order processing with stock management, and background tasks. Built with Django REST Framework.

**Project Nexus - ALX ProDev Backend Engineering Program**

**Live API:** https://ecommerce-api-wp9c.onrender.com/api/docs/

---

## Objectives

- Build a real-world backend application with RESTful API endpoints
- Apply best practices in authentication, database design, and deployment
- Demonstrate professional workflows in version control and documentation
- Implement background task processing and caching strategies

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| Django 5.1 + DRF 3.15 | Web framework & API layer |
| PostgreSQL 16 | Relational database |
| Redis 7 | Caching & message broker |
| Celery | Background task processing |
| Docker + Docker Compose | Containerized deployment |
| SimpleJWT | Token-based authentication |
| drf-yasg | Auto-generated Swagger docs |
| django-filter | Advanced query filtering |
| GitHub Actions | CI/CD pipeline |

---

## Features

**Authentication**
- Custom user model with email-based login
- JWT authentication (register, login, token refresh)
- Password change with validation
- Role-based access control (buyers vs sellers)

**Product Management**
- Full CRUD for products (sellers only)
- Slug-based URLs for SEO-friendly endpoints
- Category system with subcategory support
- Multiple product images with sort ordering
- Filtering, search, and sorting

**Reviews**
- Product reviews with 1-5 star ratings
- One review per user per product (enforced at DB level)
- Average rating calculations

**Order Processing**
- Order placement with automatic stock validation
- Stock decrements wrapped in database transactions
- Order cancellation with stock restoration
- Price snapshots in order items so history stays accurate even if products change

**Background Tasks (Celery + Redis)**
- Order confirmations - async notification on order placement
- Low stock alerts - triggered when stock drops below 5 units
- Stale order cleanup - auto-cancels pending orders older than 24hrs

**Performance**
- Redis caching on product list and category endpoints
- Database indexes on price, category, SKU, and created_at
- `select_related` / `prefetch_related` to prevent N+1 queries
- Separate lightweight serializer for list views vs detail views
- Rate limiting (50/hr anonymous, 200/hr authenticated)

---

## API Endpoints

### Authentication
```
POST   /api/v1/auth/register/         # Create account
POST   /api/v1/auth/login/            # Get JWT tokens
POST   /api/v1/auth/token/refresh/    # Refresh access token
GET    /api/v1/auth/profile/          # View profile
PUT    /api/v1/auth/profile/          # Update profile
POST   /api/v1/auth/change-password/  # Change password
```

### Products
```
GET    /api/v1/products/                       # List products (paginated, filterable)
POST   /api/v1/products/                       # Create product (sellers only)
GET    /api/v1/products/{slug}/                # Product detail
PUT    /api/v1/products/{slug}/                # Update product (owner only)
DELETE /api/v1/products/{slug}/                # Delete product (owner only)
GET    /api/v1/products/{slug}/reviews/        # Product reviews
POST   /api/v1/products/{slug}/reviews/        # Leave a review
```

### Categories
```
GET    /api/v1/categories/           # List all categories
POST   /api/v1/categories/           # Create category (admin only)
GET    /api/v1/categories/{slug}/    # Category detail
```

### Orders
```
GET    /api/v1/orders/               # My orders
POST   /api/v1/orders/place/         # Place an order
GET    /api/v1/orders/{id}/          # Order detail
POST   /api/v1/orders/{id}/cancel/   # Cancel order
```

### Filtering & Sorting
```
/api/v1/products/?min_price=20&max_price=100
/api/v1/products/?category=electronics
/api/v1/products/?in_stock=true
/api/v1/products/?search=wireless
/api/v1/products/?ordering=price

# combine them
/api/v1/products/?category=electronics&min_price=10&ordering=price&search=bluetooth
```

---

## Database Design

7 models across 3 apps: `CustomUser`, `Category`, `Product`, `ProductImage`, `Review`, `Order`, `OrderItem`.

**Design decisions:**

- **Slug-based product URLs** - cleaner API, better for SEO
- **Order item price snapshots** - `product_name` and `product_price` saved at order time so history stays accurate even if products change or get deleted
- **Database indexes** on frequently queried fields (price, category, created_at, SKU)
- **Unique constraint** on (product, user) for reviews - one review per user per product
- **Self-referencing category FK** - supports nested subcategories
- **`select_for_update()` on stock** - locks the product row during order creation so two people cant oversell the same item

See the ERD diagram linked in the deliverables section below.

---

## Project Structure

```
ecommerce-api/
├── .github/workflows/    # CI/CD pipeline
│   └── ci.yml
├── core/                 # Settings, URLs, Celery config
├── accounts/             # Custom user model, auth views, serializers
├── products/             # Products, categories, reviews, filters
├── orders/               # Order placement, order items, stock management
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Testing

24 tests covering auth flows, product CRUD, permission checks, filtering/sorting, reviews, order placement, and stock management.

```bash
# with docker
docker-compose exec web python manage.py test

# without docker
python manage.py test
```

**Test coverage:**
- Authentication - registration, login, duplicate email, password mismatch, profile access
- Products - seller CRUD, buyer restrictions, filtering, search, ordering
- Reviews - creation, duplicate prevention
- Orders - placement, stock decrements, insufficient stock, cancellation, access control

---

## Docker & CI/CD

- Docker Compose orchestrates 4 services: web, db, redis, celery
- GitHub Actions runs tests automatically on push and pull requests
- Deployed on Render with PostgreSQL

---

## Best Practices

- 3-app structure - accounts, products, orders kept separate
- Environment variables for all secrets
- Input validation and Django's built-in password validators
- Rate limiting on all endpoints
- CORS configuration for frontend integration
- Swagger docs for all endpoints
- Database transactions on order placement

---

## Project Deliverables

- [GitHub Repository](https://github.com/Ripcode1/ecommerce-api)
- [Live API](https://ecommerce-api-wp9c.onrender.com/api/docs/)
- [ERD Diagram](https://drive.google.com/file/d/1Pl60LKfmU1BrydU6BZLjd9UP7SHJA-WD/view)
- [Presentation Deck](https://drive.google.com/file/d/1sDoLRMXiQMMVVr5sriO4t66bm4ONCzQ9/view)

---

## License

MIT
