# Electrician Contractor Management System
## 🌐 Live Demo

The project is deployed and accessible online:
https://electriciancontractormanagementsystem.onrender.com


## Introduction
The Electrician Contractor Management System is a web-based application designed to manage electricians, jobs, tasks, materials, and reports efficiently. It helps contractors organize work, assign tasks, track progress, and generate reports through a user-friendly interface.

---

## Objectives
- To simplify contractor management operations  
- To maintain records of electricians, jobs, and tasks  
- To provide real-time tracking and reporting  
- To ensure secure and role-based access  

---

## Features

- Electrician Management  
- Job Management  
- Task Tracking  
- Materials Management  
- Reports  
- Login and Registration  
- Admin Profile  
- Role-Based Access Control  
- Search and Filter  
- Notifications  
- File Upload  

---

## Variables / Models Used

- User (id, name, phone, email, role, password)  
- Electrician (id, name, phone)  
- Job (id, title, location, electrician, deadline, status)  
- Task (id, name, electrician, job, status)  
- Material (id, name, quantity)  
- Report (id, job, report_file)  

---

## Technologies Used

- Python (Django)  
- SQLite  
- HTML  
- CSS  
- Bootstrap  
- JavaScript  

---

## System Requirements

### Hardware:
- Minimum 4GB RAM  
- Basic Computer/Laptop  

### Software:
- Python 3.x  
- Django  
- Web Browser (Chrome/Edge)  
- SQLite Database  

---

## Procedure to Run the Project

1. Install Python  
2. Install Django  
3. Open terminal in project folder  
4. Run the following commands:

``bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

## Project Strcuture
ElectricianContractorManagementSystem/
├── core/
├── config/
├── templates/
├── static/
├── manage.py

## WEEK-1
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

- Python 3.10.11 
- Django 5.2.6  
- SQLite 3.40.1  
- HTML5  
- CSS3  
- JavaScript (ES6)  
- Bootstrap 5.3.0  

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
### Pavan
developing and integrating the Job and Electrician Management modules. He implemented core functionalities to manage job assignments and electrician records, ensuring smooth data flow between modules. The system was enhanced to support real-time updates, including adding jobs, assigning electricians, setting locations and deadlines, and efficiently managing electrician details such as add, update, delete, and view operations.

-----
### Shravana Naik
Managed materials functionality and system integration. Developed material management features including adding materials, tracking quantity, and updating usage. Integrated all modules (Jobs, Tasks, Electricians, and Materials) to ensure smooth data flow, and synchronized frontend with backend to enable dynamic and fully functional UI operations.

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

----
### Pavan
Handled frontend development improvements, UI/UX improvements, and usability testing. Enhanced layout structure, improved color schemes and alignment, ensured smooth navigation across all pages, tested responsiveness and functionality of buttons, fixed UI issues, and prepared the system for a clean and effective demo presentation.

-----
### Shravana Naik
Handled project documentation. Prepared complete project documentation including description, features, technologies, and screenshots, and managed the GitHub repository by uploading the final working project with a well-structured README.

-----
## WEEK-5

# Final Enhancements, Security & Deployment

In Week 5, the project focused on implementing advanced features, improving system performance, and preparing the application for real-world usage. Key enhancements included role-based access control, security improvements, API optimization, file handling, and final deployment preparation. The system was refined to ensure scalability, usability, and reliability.

---

## Features Implemented

- Role-Based Access Control (Admin and Electrician)
- Electrician Task View and Status Update
- Advanced Dashboard with statistics and visual insights
- Charts for completed and pending jobs
- API Optimization (clean structure and proper responses)
- Error Handling and Validation Improvements
- Security Enhancements (password hashing, input validation, access control)
- File Upload Feature (job images and reports)
- Deployment Setup (local hosting / online hosting)
- UI Improvements and Navigation Enhancements

----

## Technologies Used

- Python (Django)
- SQLite
- HTML, CSS, Bootstrap
- JavaScript

-----

## Key Improvements

- Implemented role-based authentication for secure access control
- Enhanced dashboard with visual data representation and insights
- Optimized APIs for better performance and structured responses
- Strengthened system security with validation and protected routes
- Added file upload functionality for jobs and reports
- Improved UI design and navigation for better user experience
- Cleaned and organized code for maintainability
- Conducted final testing to ensure system stability and performance
- Prepared project for deployment and real-world usage

-----

## Contributors and Work Distribution

### Reethi K B

Handled backend development and system security. Implemented role-based access control for Admin and Electrician, designed and optimized APIs with a clean structure, ensured proper responses and error handling, and strengthened security through password hashing, input validation, and prevention of unauthorized access.

----

### Pavan

Frontend development with a focus on UI and user experience. Designed and implemented an advanced dashboard with task statistics and charts (completed vs pending jobs), improved navigation and overall interface, added meaningful error messages, and developed electrician UI features including viewing assigned tasks and updating task status using React/Angular or HTML-CSS.

----

### Shravana Naik

Handled feature integration. Implemented file upload functionality for job images and reports,performed code cleanup by removing unused code and adding comments, and completed final submission tasks including GitHub updates, screenshots, and demo preparation.

----

