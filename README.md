## WEEK-1
# Electrician Contractor Management System

This project is a web-based application designed to manage electricians, jobs, tasks, materials, and reports. It provides a structured and user-friendly interface for contractor management operations.

---

## Features

- Electrician Management  
- Job Management  
- Task Tracking  
- Materials Management  
- Reports  
- Login and Registration  
- Admin Profile  

---

## Technologies Used

- HTML  
- CSS  
- JavaScript  
- Bootstrap  

---

## Project Structure

electrician-system/

├── index.html  
├── login.html  
├── register.html  
├── dashboard.html  
├── electricians.html  
├── jobs.html  
├── tasks.html  
├── materials.html  
├── reports.html  
├── profile.html  

├── js/  
│   └── app.js  

├── images/  
│   └── electrician.jpeg  

---

## Contributors and Work Distribution

### Reethi K B

Led frontend development and UI enhancement. Redesigned the interface using Bootstrap, implemented responsive design, added JavaScript validation, and integrated all UI modules.

---

### Pavan

Developed the initial UI using HTML and CSS. Created layouts and structured the system design.

---

## WEEK-2

# Backend Integration & CRUD Functionality

In Week 2, the project was converted into a fully functional Django application with backend logic, database integration, and CRUD operations.

---

## Features Implemented

- Django Backend Setup  
- Database Integration (SQLite)  
- User Authentication (Login, Register, Logout, Forgot Password)  
- Electricians CRUD (Add, Update, Delete)  
- Jobs CRUD with deadline handling  
- Tasks CRUD with status tracking  
- Materials CRUD with quantity management  
- Dashboard with dynamic data  
- Reports with chart visualization  

---

## Technologies Used

- Python (Django)  
- SQLite  
- HTML, CSS, Bootstrap  
- JavaScript  

---

## Key Improvements

- Converted static HTML into Django templates  
- Connected frontend with backend using views and models  
- Implemented full CRUD operations  
- Fixed update issues by correcting form structure  
- Added session-based authentication  
- Used base template for consistent UI  

---

## Project Structure (Updated)

ElectricianContractorManagementSystem/

├── core/  
├── config/  
├── templates/  
├── static/  
├── manage.py  

---

## Contributors and Work Distribution

### Reethi K B

Handled complete backend creation and integration of all files. Connected frontend pages with Django backend, implemented CRUD operations, fixed update issues, and developed authentication system (login, register, forgot password).

---

### Pavan

Worked on database creation including tables (Users, Electricians, Jobs, Tasks). 

---

### Shravana

Handled authentication and dashboard functionality. Worked on login, registration.

---
## WEEK-3

# Module Development & System Integration

In Week 3, the project focused on developing core modules of the system and integrating all components into a fully functional application. The system was enhanced to handle real-time operations with proper data flow between modules.

---

## Features Implemented

- Job Management Module (Add job, assign electrician, set location & deadline, view jobs)  
- Electrician Management (Add, update, delete, view list)  
- Task Management (Assign task to electrician, link task with job)  
- Task Tracking (View tasks, filter by status, update status – Pending → Completed)  
- Materials Management (Add materials, track quantity, update usage)  
- Module Integration (Job ↔ Task ↔ Electrician ↔ Materials)  
- Fully Dynamic System (All modules connected with backend, no static data)  

---

## Technologies Used

- Python (Django)  
- SQLite  
- HTML, CSS, Bootstrap  
- JavaScript  

---

## Key Improvements

- Developed complete modules for job, task, electrician, and materials management  
- Integrated all modules to ensure smooth workflow across the system  
- Implemented task tracking with status updates  
- Ensured dynamic interaction between frontend and backend  
- Improved system structure and real-time data handling  
- Achieved full module connectivity and synchronization  


## Contributors and Work Distribution

### Reethi K B

Handled Task Management (Core Logic). Implemented task assignment, linked tasks with jobs, developed task tracking system, added status filtering, and enabled status updates (Pending → Completed).

---
## WEEK-4

# Backend & Core Functionality Enhancement

In Week 4, the project focused on enhancing backend capabilities by implementing advanced system features such as reports, search and filtering, notifications, and testing. The system was improved to provide better data tracking, real-time alerts, and overall performance.

---

## Features Implemented

- Reports Module (Daily Work Report, Task Completion Report, Electrician Activity Report)
- Search Jobs (search based on job title)
- Filter Tasks (Pending / Completed)
- Filter Electricians (search by name)
- Notification System (deadline alerts, task completion alerts, new task alerts)
- Dashboard Enhancement with dynamic alerts and data
- Backend Testing (form validation, CRUD verification, error fixing)

---

## Technologies Used

- Python (Django)
- SQLite
- HTML, CSS, Bootstrap
- JavaScript

---

## Key Improvements

- Implemented report generation using backend queries
- Added search and filter features for efficient data handling
- Developed alert system for task and job updates
- Improved dashboard with real-time notifications and summary data
- Fixed issues related to task updates and migrations
- Ensured smooth backend and frontend integration
- Completed testing of all modules and verified system functionality

---

## Contributors and Work Distribution

### Reethi K B

Handled Backend & Core Functionality. Implemented reports module, developed search and filter features, created notification system, enhanced dashboard with alerts, performed backend testing, and fixed system errors.

