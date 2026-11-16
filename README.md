<<<<<<< HEAD
# 🎓 Student Management System

A simple, modern, and fully functional **Student Management System** developed using **Python Full Stack Development (Flask, SQLite, HTML5, CSS3)**. Designed for academic project submissions and summer internship demonstrations.

---

## 🌟 Key Highlights & Features

1. **Dashboard & Summary Stats**:
   - Interactive overview cards showing Total Students, Departments Count, and SQLite Database Engine status.
   - Clean, light blue and white aesthetic tailored for university and internship evaluations.

2. **Full CRUD Operations**:
   - **Create (Add Student)**: Register student name, roll number, email, department, and phone number.
   - **Read (View Students)**: Comprehensive tabular view with styled department badges.
   - **Update (Edit Student)**: Easily update existing records with pre-populated input forms.
   - **Delete (Remove Student)**: Safely delete records with instant browser confirmation dialogs.

3. **Search & Filter Functionality**:
   - Instant search across **Roll Number**, **Student Name**, or **Department**.
   - One-click **Reset Filter** button to restore full view.

4. **Data Validation & Flash Alerts**:
   - Strict validation preventing duplicate Roll Numbers.
   - Email format verification and 10+ digit phone number checks.
   - Colored visual alert banners for Success (Green), Error (Red), and Warning (Yellow).

---

## 📁 Project Structure

```
student_management/
│
├── app.py                     # Main Flask backend application with SQLite CRUD operations
├── database.db                # SQLite database (auto-generated with sample records)
├── requirements.txt           # Python dependency specifications
│
├── templates/                 # Frontend HTML templates
│   ├── index.html             # Dashboard, summary cards, search bar, and student records table
│   ├── add_student.html       # Student registration form with validation hints
│   └── update_student.html    # Student editing form pre-filled with existing data
│
└── static/                    # Frontend styling assets
    └── style.css              # Custom responsive stylesheet (Light Blue & White theme)
```

---

## ⚙️ Installation & Requirements

### Prerequisites
- **Python 3.8 or higher** installed on your system.
- **Visual Studio Code** (recommended editor).

### Step 1: Open VS Code Terminal
Open your project folder in Visual Studio Code (`File` > `Open Folder...`). Then open an integrated terminal (`Ctrl + ~` or `Terminal` > `New Terminal`).

### Step 2: Install Flask
Run the following command in the terminal:
```bash
pip install Flask
```
*(or install from requirements.txt)*:
```bash
pip install -r student_management/requirements.txt
```

---

## 🚀 How to Run the Application in VS Code

### Option 1: Direct Execution from `student_management/`
1. In your VS Code terminal, navigate to the `student_management` folder:
   ```bash
   cd student_management
   ```
2. Run the application:
   ```bash
   python app.py
   ```
   *(On Windows with Python launcher, you can also use `py app.py`)*

### Option 2: Running from the Root Folder
Run the included launcher:
```bash
python run.py
```

### Step 3: Access the System in Your Browser
Once the terminal outputs:
```
* Running on http://127.0.0.1:5000
```
Open your web browser (Chrome, Edge, Firefox) and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**
=======
# Student-Management-System
>>>>>>> 3e7359ebbc13786f48646ee833f96cc56abc59ec
