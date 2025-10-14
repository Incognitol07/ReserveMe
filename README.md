# ReserveMe API

The **ReserveMe API** simplifies the process of booking and managing spaces, such as meeting rooms, event halls, or workspaces. It features robust user authentication, real-time availability tracking, and notifications, making it an efficient tool for both personal and professional use.

## Problem Solved

Booking spaces can be a tedious process without an organized system. The **ReserveMe API** streamlines space booking by allowing users to:

- **View and book spaces**: Check availability and book spaces in real time.
- **Manage reservations**: Update or cancel reservations seamlessly.
- **Receive notifications**: Stay informed with automated notifications for booking confirmations, reminders, and updates.
- **Secure user access**: Authenticate and manage bookings through JWT-based secure access.

## Key Features

- **User Management**: Register, log in, and authenticate users using JWT-based authentication.
- **Space Management**: Add, update, and delete spaces, including specifying amenities, capacities, and availability.
- **Real-Time Booking**: Book spaces with up-to-date availability tracking.
- **Notifications**: Receive email or in-app notifications for booking confirmations, reminders, and changes.
- **Secure Access**: Protect user and booking data with secure authentication and role-based access control.
- **Automation**: Schedule notifications and reminders for upcoming bookings.

## Tech Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based authentication
- **Notifications**: Email or in-app notification system
- **Deployment**: Docker

## Installation

### Prerequisites

- **Python 3.12+**
- **PostgreSQL** (for the database)
- **Docker** (for containerized deployment)

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/Incognitol07/ReserveMe
cd ReserveMe
```

#### 2. Set Up Virtual Environment

1. **Create the virtual environment**:

   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:

     ```cmd
     .\venv\Scripts\activate
     ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Deactivate the virtual environment (when done)**:

   ```bash
   deactivate
   ```

#### 3. Set Up Environment Variables

Create a `.env` file:

  ```cmd
  copy .env.example .env
  ```

### Running the Application

1. **Activate the virtual environment**:

   ```cmd
   .\venv\Scripts\activate
   ```

2. **Start the server**:

   ```bash
   uvicorn app.main:app --reload
   ```

3. Visit `http://127.0.0.1:8000` in your browser.

## Features Overview

### Space Management

- **Add, Update, and Delete Spaces**: Manage spaces with details such as name, capacity, location, and amenities.
- **Availability Tracking**: View real-time availability and prevent booking conflicts.

### Booking Management

- **Create, Update, and Cancel Bookings**: Handle bookings with ease, specifying time slots and additional preferences.
- **Booking Reminders**: Receive automated reminders for upcoming bookings.

## Testing the API

You can test the API using **curl**, **Postman**, or FastAPI's interactive docs at <http://127.0.0.1:8000/docs>.

## License

This project is licensed under the MIT License.
