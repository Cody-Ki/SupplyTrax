# SupplyTrax

SupplyTrax is a simple Django‑powered inventory management MVP. Track items, adjust stock levels, and manage asset check‑in/out.
Devloped based of inspiration from the likes of Snipe-IT and BlueTally.

---

## Features

- **Dashboard**: Overview of total items and low‑stock alerts  
- **Inventory CRUD**: Create, view, edit, and delete items  
- **Stock Adjustment**: Add or remove quantity for non‑asset items  
- **Asset Management**: Check‑out and check‑in individual asset serials  
- **Transaction Log**: Automatic recording of all stock and asset actions

---

## Requirements

- Python 3.10+  
- Django 5.1.7  
- SQLite (default) or another supported DB  
- `pip` for package installation  

---

## Getting Started

### 1. Clone the repo

```bash
    git clone https://github.com/your‑username/SupplyTrax.git
    cd SupplyTrax
```
### 2. Create & activate virtualevn
```bash
    python -m venv .venv
    
    # macOS / Linux
    source .venv/bin/activate
    
    # Windows (PowerShell)
    .venv\Scripts\Activate.ps1
```
### 3. Install dependencies
```bash
  pip install -r requirements.txt
```
### 4. Configuration
Open SupplyTrax/settings.py and:

DEBUG

True for development

False for production

ALLOWED_HOSTS
Add your domain(s) or IP addresses

### 5. Database setup & migrations
```bash
    python manage.py migrate
```

### 6. Create a superuser
```bash
    python manage.py createsuperuser
```

### 7. Run the Development Server
```bash
    python manage.py runserver
```
Open your browser at http://127.0.0.1:8000/

## Versioning
This project follows Semantic Versioning.

0.1.0 — Initial MVP

Future releases will increment minor/patch numbers as features are added or bugs are fixed.

