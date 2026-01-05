# 🧩 Migi Shoes Fixtures

This folder contains the **fixture data** used to test and demonstrate the main functionality of the **Migi Shoes** website.
Each `.json` file here represents data exported from the Django admin during local testing.  
They can be loaded back into the database to quickly restore a working test environment.

---

## 📁 Folder Structure

fixtures/
│
├── customer/
│ └── customers.json
│ └── notifications.json
│
├── products/
│ ├── brands.json
│ ├── shoes.json
│ └── variants.json
│
├── orders/
│ ├── orders.json
│ └── order_items.json
│
│
└── core/
  └── users.json

---

## 📘 File Descriptions

### **customer/customers.json**
Contains sample **customer profiles** used to test:
- The customer dashboard
- Profile viewing and editing
- Order and notification associations

---

### **products/**
Includes all product-related data:
- **brands.json** → List of shoe brands and their metadata (name, website, description)
- **shoes.json** → Core shoe models (base info like name, category, price, gender)
- **shoe_variants.json** → Specific variations of shoes (size, color, SKU, stock)
- **orders.json** → Sample orders made by customers for testing order history and status updates
- **order_items.json** → Items within each order, used to test totals and relationships

---

### **customer/notifications.json**
Holds customer notifications, used to test the dashboard notification system and message rendering.

---

### **core/auth_users.json**
Contains Django `User` objects for login and authentication testing.  
These credentials can be used to sign in to the **Customer Dashboard** and **Admin Panel**.

> ⚠️ Default passwords are not stored here for security reasons.  
> You can reset them via the Django admin or using the `changepassword` command.

---

## ⚙️ How to Use Fixtures

Before loading, make sure your virtual environment and migrations are up to date:

```bash
python manage.py makemigrations
python manage.py migrate

Then, load each fixture into your local database:

python manage.py loaddata fixtures/users/auth_users.json
python manage.py loaddata fixtures/customer/customers.json
python manage.py loaddata fixtures/products/brands.json
python manage.py loaddata fixtures/products/shoes.json
python manage.py loaddata fixtures/products/shoe_variants.json
python manage.py loaddata fixtures/products/orders.json
python manage.py loaddata fixtures/products/order_items.json
python manage.py loaddata fixtures/products/reviews.json
python manage.py loaddata fixtures/notifications/notifications.json


You can also load all fixtures at once:

python manage.py loaddata fixtures/*/*.json

These files were generated using:

python manage.py dumpdata app_name.ModelName --indent 4 > fixtures/app_name/filename.json


They are purely for testing and demonstration
