# Airport Management System

**CBSE Class 12 Informatics Practices Project**

A comprehensive web-based Airport Management System built with Django, MySQL, Pandas, and Matplotlib. This project demonstrates the integration of Python programming, database management, data analysis, and web development as required for CBSE Class 12 IP practical examination.

## 🎯 Project Overview

The Airport Management System provides a complete solution for managing airport operations including:

- **Flight Management**: Schedule flights, track status, manage routes
- **Passenger Management**: Register passengers, maintain records, track demographics
- **Booking System**: Create bookings, manage reservations, handle payments
- **Staff Management**: Manage airport staff, roles, and departments
- **Check-in System**: Handle passenger check-ins, baggage, and boarding
- **Reports & Analytics**: Generate insights with charts and data analysis

## 🚀 Features

### Core Functionality
- ✅ Complete CRUD operations for all entities
- ✅ User authentication and authorization
- ✅ Role-based access control (Admin/Staff/Public)
- ✅ Responsive web interface with Bootstrap
- ✅ Data validation and error handling

### CBSE IP Requirements
- ✅ **Python Programming**: Django backend with comprehensive business logic
- ✅ **Database Integration**: MySQL with proper relationships and constraints
- ✅ **Pandas**: Data analysis and manipulation for reporting
- ✅ **Matplotlib**: Charts and visualizations for insights
- ✅ **Web Development**: HTML/CSS/JavaScript frontend
- ✅ **SQL**: Complex queries, joins, views, and stored procedures

### Reports & Visualization
- 📊 Flight destination analysis (Bar charts)
- 📊 Booking status distribution (Pie charts)
- 📊 Passenger age demographics (Histograms)
- 📊 Revenue analysis by airline
- 📊 Real-time dashboard with statistics

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Django 5.2.5 |
| **Database** | MySQL 8.x |
| **Frontend** | HTML5, CSS3, Bootstrap 5 |
| **Data Analysis** | Pandas, NumPy |
| **Visualization** | Matplotlib, Chart.js |
| **Authentication** | Django Auth System |
| **Deployment** | Development Server |

## 📋 Prerequisites

Before running this project, ensure you have:

1. **Python 3.8+** installed on your system
2. **MySQL Server 8.0+** running
3. **Git** (optional, for cloning)
4. **Web browser** (Chrome, Firefox, Safari, Edge)

## 🔧 Installation & Setup

### Step 1: Clone or Download the Project
```bash
# Option 1: Clone from repository
git clone <repository-url>
cd airport-management-system

# Option 2: Extract downloaded ZIP file
# Navigate to the extracted folder
```

### Step 2: Set up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Install required packages
pip install django mysqlclient pandas matplotlib numpy
```

### Step 4: Configure MySQL Database
1. **Start MySQL Server**
2. **Create Database:**
   ```sql
   CREATE DATABASE airport_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. **Update Database Settings:**
   - Open `airport_mgmt/settings.py`
   - Update the `DATABASES` configuration with your MySQL credentials:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'airport_management',
           'USER': 'your_mysql_username',
           'PASSWORD': 'your_mysql_password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

### Step 5: Run Database Migrations
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser
```bash
# Create admin account
python manage.py createsuperuser
# Follow prompts to set username, email, and password
```

### Step 7: Load Sample Data
```bash
# Create sample data for testing
python create_sample_data.py
```

### Step 8: Run the Development Server
```bash
# Start Django development server
python manage.py runserver
```

### Step 9: Access the Application
- **Website**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 👥 Default Login Credentials

### Admin Account
- **Username**: admin
- **Password**: admin

### Staff Accounts
- **Username**: pilot1 | **Password**: staff123
- **Username**: crew1 | **Password**: staff123
- **Username**: ground1 | **Password**: staff123

## 📊 Data Analysis & Visualization

### Running Data Analysis
```bash
# Generate comprehensive analysis and charts
python data_analysis.py
```

This will create:
- `airport_analysis_dashboard.png` - Combined dashboard
- `destinations_chart.png` - Flight destinations analysis
- `age_distribution_chart.png` - Passenger demographics
- `airport_summary_report.txt` - Detailed text report

### Sample Analysis Features
- Flight destination popularity
- Passenger age distribution
- Booking status breakdown
- Revenue analysis by airline
- Staff distribution by role
- Check-in statistics

## 🗂️ Project Structure

```
airport-management-system/
├── airport_mgmt/              # Django project settings
│   ├── __init__.py
│   ├── settings.py           # Configuration
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI config
├── core/                     # Main application
│   ├── migrations/          # Database migrations
│   ├── __init__.py
│   ├── admin.py            # Admin configuration
│   ├── apps.py             # App configuration
│   ├── forms.py            # Django forms
│   ├── models.py           # Database models
│   ├── urls.py             # URL patterns
│   └── views.py            # View functions
├── templates/               # HTML templates
│   ├── core/               # App-specific templates
│   ├── registration/       # Auth templates
│   └── base.html           # Base template
├── static/                 # Static files (CSS, JS, images)
├── venv/                   # Virtual environment
├── manage.py               # Django management script
├── create_sample_data.py   # Sample data generator
├── data_analysis.py        # Data analysis script
├── database_setup.sql      # MySQL setup script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 📑 Database Schema

### Core Tables
1. **Flights** - Flight schedules and information
2. **Passengers** - Passenger personal details
3. **Bookings** - Flight reservations
4. **Staff** - Airport staff information
5. **CheckIns** - Passenger check-in records

### Relationships
- Bookings → Passengers (Many-to-One)
- Bookings → Flights (Many-to-One)
- CheckIns → Bookings (One-to-One)
- Staff → Users (One-to-One)

## 🔍 Key Features Demonstration

### 1. Public Features
- View flight schedules
- Search flights by route/date
- Flight details and information

### 2. Staff Features
- Manage passengers
- Create and manage bookings
- Handle check-ins
- View comprehensive reports

### 3. Admin Features
- Full system administration
- User and staff management
- System configuration
- Data analysis and reports

## 📈 CBSE IP Practical Compliance

### Required Components ✅
- [x] **Python Programming**: Django framework, business logic
- [x] **Database Connectivity**: MySQL integration with Django ORM
- [x] **Data Handling**: Pandas for analysis, data manipulation
- [x] **Visualization**: Matplotlib charts, web-based graphs
- [x] **Web Development**: HTML, CSS, JavaScript, Bootstrap
- [x] **SQL Operations**: CRUD operations, complex queries
- [x] **User Interface**: Responsive design, forms, navigation
- [x] **Data Validation**: Form validation, error handling
- [x] **Integration**: Complete system integration

### Practical File Requirements ✅
- [x] **Source Code**: Complete Django project
- [x] **Database**: MySQL with sample data
- [x] **Documentation**: Comprehensive README
- [x] **Screenshots**: Web interface captures
- [x] **Analysis Scripts**: Pandas/Matplotlib code
- [x] **Test Data**: Sample flights, passengers, bookings

## 🔧 Troubleshooting

### Common Issues

1. **MySQL Connection Error**
   ```
   Solution: Check MySQL service is running and credentials are correct
   ```

2. **Module Not Found Error**
   ```bash
   # Ensure virtual environment is activated
   pip install -r requirements.txt
   ```

3. **Migration Issues**
   ```bash
   # Reset migrations if needed
   python manage.py migrate --run-syncdb
   ```

4. **Static Files Not Loading**
   ```bash
   # Collect static files
   python manage.py collectstatic
   ```

## 📱 Screenshots

### Homepage
- Welcome dashboard with statistics
- Quick navigation to all features
- Recent flights display

### Flight Management
- Comprehensive flight listing
- Search and filter capabilities
- Detailed flight information

### Booking System
- Easy booking creation
- Passenger selection
- Seat management

### Reports Dashboard
- Interactive charts
- Data analysis insights
- Export capabilities

## 🎓 Learning Outcomes

This project demonstrates:

1. **Full-Stack Development**: Backend and frontend integration
2. **Database Design**: Proper normalization and relationships
3. **Data Analysis**: Using Pandas for insights
4. **Visualization**: Creating meaningful charts with Matplotlib
5. **Web Technologies**: Modern responsive design
6. **Software Engineering**: Proper project structure and documentation

## 📝 Future Enhancements

- Payment gateway integration
- Email notifications
- Mobile app development
- Advanced analytics
- Real-time flight tracking
- Multi-language support

## 📄 License

This project is created for educational purposes as part of CBSE Class 12 Informatics Practices curriculum.

## 👨‍💻 Author

**[Your Name]**  
CBSE Class 12 Informatics Practices Project  
Academic Year: 2024-25

---

**Note**: This project is designed specifically for CBSE Class 12 IP practical examination and includes all required components as per the latest curriculum guidelines.
