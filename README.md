# ReserveMe API

The **ReserveMe API** simplifies the process of booking and managing spaces, such as meeting rooms, event halls, or workspaces. It features robust user authentication, real-time availability tracking, and notifications, making it an efficient tool for both personal and professional use.

---

## Problem Solved

Booking spaces can be a tedious process without an organized system. The **ReserveMe API** streamlines space booking by allowing users to:

* **View and book spaces**: Check availability and book spaces in real time.
* **Manage reservations**: Update or cancel reservations seamlessly.
* **Receive notifications**: Stay informed with automated notifications for booking confirmations, reminders, and updates.
* **Secure user access**: Authenticate and manage bookings through JWT-based secure access.

---

## Key Features

* **User Management** — JWT-based authentication for registration and login
* **Space Management** — Add, update, and delete spaces with metadata
* **Real-Time Booking** — Book with up-to-date availability tracking
* **Notifications** — Email or in-app booking updates
* **Secure Access** — Role-based access control
* **Automation** — Scheduled reminders for upcoming bookings

---

## Tech Stack

| Layer                  | Technology                     |
| ---------------------- | ------------------------------ |
| **Backend Framework**  | FastAPI                        |
| **Database**           | PostgreSQL with SQLAlchemy ORM |
| **Authentication**     | JWT                            |
| **Deployment**         | Docker                         |
| **Package Management** | `uv` (by Astral)               |

---

## Installation

### Prerequisites

* **Python 3.12+**
* **PostgreSQL** (for database)
* **Docker** *(optional, for containerized deployment)*
* **uv** (Python package manager) → [Install here](https://docs.astral.sh/uv/getting-started/)

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Incognitol07/ReserveMe
cd ReserveMe
```

---

### 2️⃣ Set Up Environment

1. **Sync dependencies and create virtual environment:**

   ```bash
   uv sync
   ```

   `uv` automatically handles your virtual environment (no need for `venv`).

---

### 3️⃣ Set Up Environment Variables

Copy the example `.env`:

```bash
copy .env.example .env
```

Update the values inside `.env` as needed.

---

## Running the Application

1. **Start the FastAPI server:**

   ```bash
   uv run uvicorn app.main:app --reload
   ```

2. Open your browser at **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## Testing the API

You can test the API using:

* **FastAPI Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **curl** or **Postman**

---

## License

This project is licensed under the **MIT License**.
