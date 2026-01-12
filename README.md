Plan: Django REST Framework RealWorld API Backend
Implement a RealWorld-style API (Conduit backend) in the existing django-rest-framework-realworld folder using Django 5.x, DRF, and MySQL. The workspace already has Django 6.0.1 and DRF 3.16.1 available in the tutorial virtual environment.

1. Project & App Structure
django-rest-framework-realworld/
├── manage.py
├── requirements.txt
├── conduit/                    # Project config
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── authentication/             # Custom User + JWT auth
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── backends.py             # JWT auth backend
│   └── renderers.py
├── profiles/                   # User profiles + following
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
└── articles/                   # Articles, Comments, Tags
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    └── renderers.py

2. Required Settings Changes
Configure conduit/settings.py with:

Custom User model: AUTH_USER_MODEL = 'authentication.User'
MySQL database: Use django.db.backends.mysql with mysqlclient driver
Installed apps: Add rest_framework, authentication, profiles, articles
REST Framework config: Custom renderers, JWT auth class, pagination, exception handling
CORS headers: Add django-cors-headers for frontend compatibility
3. Models & Relationships
Model	App	Key Fields	Relationships
User	authentication	email (unique), username, password, bio, image	-
Profile	profiles	user, bio, image	OneToOne → User; ManyToMany follows (self-referential)
Article	articles	slug, title, description, body, created_at, updated_at	ForeignKey → User (author); ManyToMany → Tag; ManyToMany → User (favorites)
Comment	articles	body, created_at, updated_at	ForeignKey → Article; ForeignKey → User (author)
Tag	articles	tag (unique)	ManyToMany ← Article
4. API Responsibilities per Endpoint
Endpoint	Method	Responsibility
/api/users	POST	Register new user
/api/users/login	POST	Authenticate, return JWT
/api/user	GET/PUT	Get/update current user (auth required)
/api/profiles/:username	GET	Get public profile
/api/profiles/:username/follow	POST/DELETE	Follow/unfollow user
/api/articles	GET/POST	List articles (with filters), create article
/api/articles/feed	GET	Get followed users' articles
/api/articles/:slug	GET/PUT/DELETE	CRUD single article
/api/articles/:slug/favorite	POST/DELETE	Favorite/unfavorite
/api/articles/:slug/comments	GET/POST	List/create comments
/api/articles/:slug/comments/:id	DELETE	Delete comment
/api/tags	GET	List all tags
5. Implementation Order
Project setup — Create Django project conduit, configure MySQL, add requirements.txt
Authentication app — Custom User model with email login, JWT token generation, registration/login views
Profiles app — Profile model, follow/unfollow logic, profile serializer
Articles app (core) — Article, Tag, Comment models with relationships
Article serializers & views — CRUD endpoints, filtering, pagination
Favorites & Feed — Add favorite/unfavorite actions, implement feed endpoint
Comments endpoints — Comment CRUD nested under articles
Tags endpoint — Simple list view for all tags
Final wiring — Connect all URLs to main router, add permissions, test
Files to Create
File	Purpose
manage.py	Django management script
requirements.txt	Dependencies: Django, DRF, mysqlclient, PyJWT, django-cors-headers
conduit/settings.py	MySQL config, custom user, DRF settings
conduit/urls.py	Root URL router including /api/ namespace
authentication/models.py	Custom User model with AbstractBaseUser
authentication/serializers.py	Registration, login, user serializers
authentication/views.py	RegistrationAPIView, LoginAPIView, UserRetrieveUpdateAPIView
authentication/backends.py	JWT authentication backend
profiles/models.py	Profile with follow ManyToMany
profiles/views.py	ProfileRetrieveAPIView, FollowAPIView
articles/models.py	Article, Comment, Tag models
articles/serializers.py	Article, Comment, Tag serializers with nested author
articles/views.py	ArticleViewSet, CommentViewSet, TagListAPIView

# django-rest-framework-realworld
Plan: RealWorld API — Phase 1: Project Setup
Based on your decisions, here's the refined plan for Phase 1: Django Project Initialization with MySQL.

Phase 1 Scope
Create the Django 5.x project skeleton, configure MySQL, and establish the basic app structure without authentication.

Steps
Create requirements.txt in django-rest-framework-realworld with Django 5.x, djangorestframework, mysqlclient, and django-cors-headers only (no JWT packages).

Initialize Django project — Run django-admin startproject conduit . to create manage.py and conduit/ config folder.

Create three apps — Run python manage.py startapp for users, articles, and profiles apps.

Configure conduit/settings.py:

Set DATABASES to MySQL backend with placeholder credentials
Add rest_framework, corsheaders, users, articles, profiles to INSTALLED_APPS
Configure REST_FRAMEWORK dict with pagination settings
Add CORS middleware configuration
Create empty model stubs in each app's models.py as placeholders for Phase 2.

Wire up conduit/urls.py with /api/ prefix and include paths for users, articles, and tags endpoints.

Files to Create/Modify — Phase 1
File	Action
requirements.txt	Create
manage.py	Create (via django-admin)
conduit/__init__.py	Create (via django-admin)
conduit/settings.py	Create + configure MySQL & DRF
conduit/urls.py	Create + wire API routes
conduit/wsgi.py	Create (via django-admin)
conduit/asgi.py	Create (via django-admin)
users/__init__.py, models.py, views.py, urls.py, etc.	Create (via startapp)
articles/__init__.py, models.py, views.py, urls.py, etc.	Create (via startapp)
profiles/__init__.py, models.py, views.py, urls.py, etc.	Create (via startapp)
