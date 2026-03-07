# Connectly API

## Project Overview
Connectly API is a Django REST Framework project that implements core social media features such as user authentication, post creation, likes, comments, Google OAuth login, and a personalized news feed with sorting and pagination.

This project was developed as part of a coursework series focused on API design, authentication, third-party integration, and efficient data handling.

---

## Features
- User authentication with token-based login
- Google OAuth login integration
- Create and manage posts
- Like posts
- Add and retrieve comments
- News feed endpoint
- Sorting posts by date
- Pagination for efficient feed retrieval

---

## Technologies Used
- Python
- Django
- Django REST Framework
- SQLite
- SimpleJWT
- Google OAuth / third-party authentication library

---

## API Endpoints

### Authentication
- `POST /api/token/` — obtain JWT token
- `POST /api/token/refresh/` — refresh token
- `POST /auth/google/login` — login using Google OAuth

### Posts
- `GET /posts/`
- `POST /posts/`
- `GET /posts/<id>/`

### Likes and Comments
- `POST /posts/<id>/like/`
- `POST /posts/<id>/comment/`
- `GET /posts/<id>/comments/`

### News Feed
- `GET /feed/` — retrieve paginated and sorted user feed

---

## News Feed Behavior
The news feed endpoint retrieves posts in descending order by creation date. Pagination is applied to limit the number of posts returned per request. Optional filtering logic may also be used, such as prioritizing posts from followed users or other user-specific conditions.

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repository-url>
cd <your-repository-folder>

### Testing
The API was tested using Postman.

### AI Disclosure Statement
This project was completed with the assistance of AI tools for learning support, code explanation, debugging guidance, documentation drafting, and diagram planning. All final implementation decisions, testing, review, and submission preparation were performed by the student. 

### Author
Mhery Dela Paz