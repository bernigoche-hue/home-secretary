# Home Secretary – Family Event Management Platform

## Overview

The Home Secretary is a web-based family coordination platform developed using Python and Flask. It enables members of a family to organise shared events, assign household tasks, and coordinate shopping activities from a single secure application.

The prototype was developed as part of a Software Engineering assessment using an Agile Scrum development approach and implements the Home Secretary case study involving the Beecham family.

---

## Features

### User Management

- User registration
- Secure login
- Logout
- Password hashing
- Session management

### Family Group Management

- Create a family group
- Join a family group using an invitation code
- Administrator and member roles
- Shared family workspace

### Event Management

- Create family events
- View shared events
- Edit events
- Delete events

### Household Task Management

- Create household tasks
- Assign tasks to family members
- Track task status
- Edit tasks
- Delete tasks

### Shared Shopping List

- Create shopping items
- Edit shopping items
- Delete shopping items
- Mark shopping items as purchased
- Restore purchased items

---

## Technologies Used

- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- SQLite
- Bootstrap 5
- HTML5
- CSS3
- Jinja2

---

## Project Structure

```text
home-secretary/
│
├── app/
│   ├── templates/
│   ├── static/
│   ├── models.py
│   ├── routes.py
│   ├── forms.py
│   └── __init__.py
│
├── instance/
├── tests/
├── run.py
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/bernigoche-hue/home-secretary.git
```

Move into the project folder:

```bash
cd home-secretary
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment.

### macOS/Linux

```bash
source venv/bin/activate
```

### Windows

```cmd
venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python run.py
```

Open your browser and visit:

```
http://127.0.0.1:5000
```

---

## Agile Development

The project was developed using four Scrum sprints.

| Sprint | Features Delivered |
|---------|--------------------|
| Sprint 1 | Authentication and Family Group Management |
| Sprint 2 | Event Management |
| Sprint 3 | Household Task Management |
| Sprint 4 | Shared Shopping List |

---

## Future Enhancements

Potential future improvements include:

- GPS proximity reminders
- Push notifications
- Smart home integration
- Smart refrigerator integration
- Mobile application
- Cloud deployment

---

## Author

Home Secretary Prototype

Software Engineering Assessment

University of Derby
