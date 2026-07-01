# Hospital Management Backend API

A robust, simple, and clean Django REST Framework backend designed with a **hierarchy-based role permissions (RBAC)** model for Hospital management.

## Tech Stack
- **Python** (version 3.14+)
- **Django** (version 5.0+)
- **Django REST Framework** (DRF)
- **SimpleJWT** (JSON Web Tokens)
- **Django Filters** (Advanced search, ordering, and reports)
- **SQLite** (Default database for simple setups) with **PostgreSQL** compatibility.

---

## Role-Based Access Control (RBAC) & Hierarchy

The application enforces a strict hierarchical security model:

```
Super Admin (Global access)
   └── Headquarters (HQ Admin/Staff)
         └── Sub Headquarters (Sub HQ Staff)
               └── Medical Representative (MR)
```

1. **Super Admin**:
   - Full access to manage all HQs, Sub HQs, Users (HQ Admins, HQ Staff, Sub HQ Staff, MRs), Doctors, Visits, and reports.
   - Access to global dashboard APIs.
2. **HQ Admin**:
   - Manage HQ Staff, Sub HQs, Sub HQ Staff, and MRs under their assigned HQ.
   - Access HQ-level dashboard and reports.
3. **HQ Staff**:
   - Manage Doctors, Visits, and Reports directly under their own Headquarters.
4. **Sub HQ Staff**:
   - Manage Doctors and Daily Visit Reports under their assigned Sub Headquarters.
5. **Medical Representative (MR)**:
   - View assigned Doctors.
   - Mark visits (daily reports) for assigned doctors.
   - View their own visits list.

---

## Setup & Running the Application

### 1. Prerequisites
Ensure you have Python 3.14 or later installed on your system.

### 2. Install Dependencies
Create a virtual environment, activate it, and install required packages:
```bash
# Create Virtual Environment
python -m venv venv

# Activate Virtual Environment (Windows)
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Environment Configurations
Rename `.env.example` to `.env` or run:
```bash
cp .env.example .env
```
*(By default, this sets SQLite as the active database. If you wish to use PostgreSQL, uncomment and adjust the PostgreSQL variables in `.env`)*

### 4. Database Migrations
Create the database tables and apply migrations:
```bash
python manage.py migrate
```

### 5. Seed Mock Data
We have provided a custom CLI command to instantly populate the database with complete HQs, Sub HQs, hierarchical users, assigned doctors, and visits:
```bash
python manage.py seed_data
```

### 6. Start the Server
Run the local development server:
```bash
python manage.py run server
# or
python manage.py runserver
```
The API will be live at `http://127.0.0.1:8000/`.

---

## Running Automated Tests
Run the comprehensive suite of tests checking JWT authentication, role restrictions, and dashboard computations:
```bash
python manage.py test
```

---

## Seeding Credentials Summary
After running `python manage.py seed_data`, you can authenticate at the `/api/token/` endpoint with any of these users (the password is the same as the username):

| Role | Username | Password |
|---|---|---|
| **Super Admin** | `superadmin` | `superadminpassword` |
| **Ahmedabad HQ Admin** | `ahmedabad_admin` | `ahmedabad_admin` |
| **Ahmedabad HQ Staff** | `ahmedabad_staff` | `ahmedabad_staff` |
| **Satellite Sub HQ Staff** | `satellite_staff` | `satellite_staff` |
| **Satellite MR** | `satellite_mr` | `satellite_mr` |
| **Maninagar Sub HQ Staff** | `maninagar_staff` | `maninagar_staff` |
| **Maninagar MR** | `maninagar_mr` | `maninagar_mr` |
| **Surat HQ Admin** | `surat_admin` | `surat_admin` |
| **Surat HQ Staff** | `surat_staff` | `surat_staff` |
| **Adajan MR** | `adajan_mr` | `adajan_mr` |

---

## Testing with Postman
We have provided a Postman collection (`hospital_api_postman_collection.json`) in the root directory.
1. Import this file into Postman.
2. Select any request inside the collection.
3. Call the `Obtain JWT Token` request inside the `Authentication` folder with valid credentials. It will automatically capture and save the `access_token` into a collection variable called `{{token}}`.
4. All other API calls in the collection will dynamically use this token for Authorization.
