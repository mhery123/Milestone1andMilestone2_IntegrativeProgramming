Connectly API

Connectly API is a Django REST Framework project that includes user authentication, post creation, likes, comments, Google OAuth login, a news feed with sorting and pagination, and privacy settings with role-based access control.

Project Features

User authentication with JWT
Google OAuth login
Create and retrieve posts
Like posts
Add and retrieve comments
News feed endpoint
Sorting by date
Pagination
Privacy settings for posts
Role-Based Access Control (RBAC)

Technologies Used

Python
Django
Django REST Framework
SQLite
SimpleJWT
Google OAuth integration

API Endpoints
Authentication

POST /api/token/
POST /api/token/refresh/
POST /auth/google/login

Posts

GET /posts/
POST /posts/
GET /posts/<id>/

Likes and Comments

POST /posts/<id>/like/
POST /posts/<id>/comment/
GET /posts/<id>/comments/

News Feed

GET /feed/

Privacy Settings and RBAC

Posts now support privacy settings to control visibility. Public posts are visible to all users. Private posts are visible only to the post owner. Friends-only posts are visible to approved connections. Role-Based Access Control restricts certain actions based on the user's assigned role such as admin or regular user. Permissions are enforced at the view level using custom permission classes.

Setup

Clone the repository git clone
Go to the project folder cd
Create a virtual environment python -m venv venv
Activate the virtual environment
Windows: venv\Scripts\activate
Mac/Linux: source venv/bin/activate
Install dependencies pip install -r requirements.txt
Apply migrations python manage.py migrate
Run the server python manage.py runserver

Testing

The API was tested using Postman for:

Authentication
Protected endpoints
Likes and comments
Duplicate like validation
Comment validation
Google OAuth login
News feed retrieval
Sorting and pagination
Invalid parameter handling
Privacy settings enforcement
Role-based access control

AI Disclosure Statement

AI tools were used in this project as a learning aid for debugging support, clarifying technical concepts, improving documentation, and planning diagrams. The final implementation, testing, and submission preparation were completed and reviewed by the student.

Author

Mhery Dela Paz