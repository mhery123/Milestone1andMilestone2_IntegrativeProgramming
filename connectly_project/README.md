# Connectly API

Connectly API is a Django REST Framework project that includes user authentication, post creation, likes, comments, Google OAuth login, and a news feed with sorting and pagination.

Project features
- User authentication with JWT
- Google OAuth login
- Create and retrieve posts
- Like posts
- Add and retrieve comments
- News feed endpoint
- Sorting by date
- Pagination

Technologies used
- Python
- Django
- Django REST Framework
- SQLite
- SimpleJWT
- Google OAuth integration

API endpoints

Authentication
- POST /api/token/
- POST /api/token/refresh/
- POST /auth/google/login

Posts
- GET /posts/
- POST /posts/
- GET /posts/<id>/

Likes and Comments
- POST /posts/<id>/like/
- POST /posts/<id>/comment/
- GET /posts/<id>/comments/

News Feed
- GET /feed/

Setup

1. Clone the repository
git clone <repository-url>

2. Go to the project folder
cd <repository-folder>

3. Create a virtual environment
python -m venv venv

4. Activate the virtual environment

Windows
venv\Scripts\activate

Mac/Linux
source venv/bin/activate

5. Install dependencies
pip install -r requirements.txt

6. Apply migrations
python manage.py migrate

7. Run the server
python manage.py runserver

Testing

The API was tested using Postman for:
- authentication
- protected endpoints
- likes and comments
- duplicate like validation
- comment validation
- Google OAuth login
- news feed retrieval
- sorting and pagination
- invalid parameter handling

AI Disclosure Statement

AI tools were used in this project as a learning aid for debugging support, clarifying technical concepts, improving documentation, and planning diagrams. The final implementation, testing, and submission preparation were completed and reviewed by the student.

Author
Mhery Dela Paz