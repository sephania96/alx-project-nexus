# Project Nexus

A secure, real-time online polling system built with Django and PostgreSQL, featuring student authentication, robust API endpoints, and continuous deployment to Heroku.

---

## 🚀 Features

- **Student Authentication:** Students log in with index number and PIN (securely hashed).
- **Poll Management:** Create, update, and delete polls with multiple options.
- **Voting System:** Each student can vote only once per poll.
- **Real-Time Results:** Live vote counts and percentages for each poll option.
- **RESTful API:** Clean, well-documented endpoints (Swagger/OpenAPI).
- **Admin Panel:** Manage polls, options, and students.
- **Error Handling:** Clear, consistent error messages.
- **CI/CD:** Automated testing and deployment via GitHub Actions.
- **Deployed on Heroku:** Accessible from anywhere.

---

## 🛠️ Tech Stack

- **Backend:** Django, Django REST Framework
- **Database:** PostgreSQL (Heroku)
- **Authentication:** Custom Student model with PIN hashing
- **API Docs:** drf-yasg (Swagger/OpenAPI)
- **CI/CD:** GitHub Actions
- **Deployment:** Heroku

---

## 📦 Setup & Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/sephania96/alx-project-nexus.git
    cd project-nexus
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment variables:**
    - Create a `.env` file or set variables in your environment:
      ```
      SECRET_KEY=your-secret-key
      DEBUG=True
      DATABASE_URL=postgres://user:password@localhost:5432/poll_system
      ```

5. **Apply migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6. **Create a superuser (for admin access):**
    ```bash
    python manage.py createsuperuser
    ```

7. **Run the development server:**
    ```bash
    python manage.py runserver
    ```

---

## 🌐 API Endpoints

| Endpoint                              | Method | Description                        |
|----------------------------------------|--------|------------------------------------|
| `/api/polls/`                         | GET    | List all polls                     |
| `/api/polls/`                         | POST   | Create a new poll                  |
| `/api/polls/<id>/`                    | GET    | Retrieve poll details              |
| `/api/polls/<id>/results/`            | GET    | Get real-time poll results         |
| `/api/polls/student/login/`           | POST   | Student login (index & PIN)        |
| `/api/polls/student-vote/`            | POST   | Student vote (index, PIN, option)  |
| `/api/polls/user-votes/`              | GET    | Get user's voting history          |
| `/api/polls/my-polls/`                | GET    | Get polls created by current user  |

- **API Docs:**  
  - Swagger UI: `/swagger/`
  - ReDoc: `/redoc/`
- **Admin Panel:** `/admin/`

---

## 🧪 Running Tests

```bash
python manage.py test

## Collaboration Hub

Collaboration is key to success. Learners are encouraged to:

### Collaborate With

- **Fellow ProDev Frontend Learners**: Exchange ideas, build cohesive systems, and maximize collective output.
- **ProDev Backend Learners**: Work together to solve problems and share knowledge.

### Where to Collaborate

- **Discord Channel**: `#ProDevProjectNexus`
  - Connect with both Frontend and Backend learners.
  - Share ideas, ask questions, and get updates from staff.

💡 **ProDev Tip!**

- Use the first week to communicate your project.
- Identify frontend collaborators early for smooth integration.

---

> **Repository**: [alx-project-nexus](https://github.com/sephania96/alx-project-nexus)

> Commit and push your README.md with proper markdown formatting.
