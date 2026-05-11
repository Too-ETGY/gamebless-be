# GameBless Backend

An AI-assisted anti-online-gambling platform designed to help users reduce compulsive gambling behavior through intervention, monitoring, and positive distraction mechanisms. The system detects and identifies suspected gambling websites using a continuously updated domain database and user-submitted reports, then interrupts access by displaying a mandatory intervention popup that cannot simply be dismissed, while still allowing users to safely exit the site. To redirect user attention, the platform provides a distraction menu containing curated positive content such as news articles, educational readings, and motivational videos, accessible through quick-access floating shortcuts. The application also includes behavioral tracking features such as daily reports, access attempt monitoring, and streak systems that reward users for avoiding gambling sites over time. In addition, a dedicated chatbot application powered by AI acts as a supportive companion for conversation, emotional support, and long-term engagement.

Built with Flutter for the frontend, FastAPI for backend orchestration, Firestore for scalable realtime cloud storage, and Gemini AI for conversational intelligence, the project combines behavioral intervention, AI assistance, and digital wellbeing strategies into a unified system aimed at supporting healthier online habits.

This repository contains the backend API for GameBless, handling user authentication, profile management, behavioral tracking, and AI-powered chatbot interactions.

## Features

- **User Authentication & Sync**: Integrates with Firebase Auth for Google OAuth login and profile synchronization.
- **Behavioral Tracking**: Monitors access attempts, streaks, and points for gambling site avoidance.
- **AI Chatbot**: Powered by Gemini AI for supportive conversations and emotional support.
- **Profile Management**: User profiles with optional fields like birth date, location, gender, and occupation.
- **Scalable Storage**: Uses Firestore for real-time data storage and retrieval.
- **API Endpoints**: RESTful APIs for syncing users, fetching profiles, and managing progress.

## Tech Stack

- **Backend**: FastAPI (Python async web framework)
- **Database**: Firestore (NoSQL cloud database)
- **Authentication**: Firebase Auth
- **AI**: Gemini AI (for chatbot)
- **Frontend**: Flutter (separate repo)
- **Deployment**: Designed for cloud deployment (e.g., Google Cloud)

## Project Structure

```
gamebless-be/
├── run.bat                 # Windows batch script to run the server
├── requirements.txt        # Python dependencies
├── app/
│   ├── main.py             # FastAPI app entry point
│   ├── dependencies.py     # Dependency injection setup
│   ├── api/
│   │   └── v1/
│   │       ├── router.py   # API router for v1 endpoints
│   │       └── endpoints/
│   │           ├── auth.py # Authentication endpoints (sync, /me)
│   │           └── health.py # Health check endpoint
│   ├── core/
│   │   ├── config.py       # App configuration (settings)
│   │   ├── exceptions.py   # Custom exception handlers
│   │   ├── logging.py      # Logging setup
│   │   ├── middleware.py   # Request logging middleware
│   │   └── response.py     # Response utilities
│   ├── db/
│   │   ├── firebase.py     # Firebase initialization and client
│   │   └── repositories/
│   │       └── user_repo.py # User data repository (CRUD operations)
│   ├── models/
│   │   └── user.py         # Pydantic models for UserProfile and AccountStats
│   ├── schemas/
│   │   ├── auth.py         # API request/response schemas
│   │   └── common.py       # Common response schemas
│   ├── services/
│   │   ├── auth_service.py # Business logic for auth and user management
│   │   └── ai-service/     # AI chatbot service (placeholder)
│   └── utils/              # Utility functions
```

## Prerequisites

- Python 3.8+
- Firebase project with Firestore enabled
- Google Cloud credentials (service account key)
- Gemini AI API key (for chatbot features)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd gamebless-be
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Create a `.env` file in the root directory.
   - Add your Firebase credentials and Gemini API key:
     ```
     FIREBASE_CREDENTIALS_PATH=path/to/firebase/serviceAccountKey.json
     GEMINI_API_KEY=your-gemini-api-key
     ```

5. **Initialize Firebase**:
   - Ensure your Firebase project is set up with Firestore.
   - Place the service account key JSON file in the specified path.

## How to Run

1. **Activate the virtual environment** (if not already):
   ```bash
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

2. **Run the FastAPI server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   - Or use the provided `run.bat` on Windows:
     ```bash
     run.bat
     ```

3. **Access the API**:
   - OpenAPI docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

## API Endpoints

- `POST /api/v1/auth/sync`: Sync user profile on login/update.
- `GET /api/v1/auth/me`: Get current user profile.
- `GET /api/v1/health`: Health check.

For detailed API specs, visit the OpenAPI docs at `/docs`.

## Usage

- **Sync User**: On frontend login, send user data to `/sync` to create/update the profile.
- **Fetch Profile**: Use `/me` to retrieve user data for the profile screen.
- **Chatbot**: Integrate with Gemini AI for conversational support (expand in `ai-service/`).

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit changes: `git commit -am 'Add your feature'`.
4. Push to the branch: `git push origin feature/your-feature`.
5. Submit a pull request.

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Documentation

For more details, see the [project docs note](https://docs.google.com/document/d/1PB2TSahqv3WynVsbE8c9r_ugbk1ZUrAUeVufo0nDRDU/edit?tab=t.0).

## Contact

For questions or support, reach out to the maintainers.