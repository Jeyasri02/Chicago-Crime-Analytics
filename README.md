# Chicago Crime Analytics

## 📌 Project Overview

**Chicago Crime Analytics** is a web-based crime data analysis application developed using Python and Flask. The project focuses on analyzing Chicago crime records and presenting meaningful insights through data visualization.

The application allows users to manage crime records using **CRUD operations** and analyze crime patterns using different graphs and statistical visualizations.

The main purpose of this project is to transform crime data into useful information that can help identify **crime trends, time-based patterns, arrests, and outliers**.

## 🎯 Objectives

- Analyze Chicago crime data.
- Store and manage crime records in a database.
- Perform CRUD operations on the Crime table.
- Analyze crime patterns based on time and date.
- Generate graphical visualizations from crime data.
- Identify outliers in the dataset.
- Provide meaningful insights from the generated graphs.
- Develop a simple and user-friendly crime analytics application.

## 🛠️ Technologies Used

- **Python**
- **Flask**
- **SQLAlchemy**
- **SQLite**
- **HTML**
- **CSS**
- **Jinja2**
- **Matplotlib / Data Visualization Libraries**
- **Pandas**
- **Virtual Environment (.venv)**

## 📂 Project Structure

```text
Chicago-Crime-Analytics/
│
├── __pycache__/
│
├── .venv/
│
├── data/
│   └── Crime dataset files
│
├── instance/
│   └── chicago_crime.db
│
├── reports/
│   └── Generated reports
│
├── static/
│   ├── charts/
│   │   └── Generated chart files
│   │
│   └── CSS/
│       └── style.css
│
├── templates/
│   └── HTML template files
│
├── analysis.py
├── app.py
├── charts.py
├── config.py
├── data_loader.py
├── database.py
├── extensions.py
├── load_charts.py
├── models.py
├── routes.py
│
├── requirements.txt
└── README.md
```

## 📁 Description of Important Files

| File / Folder | Description |
|---|---|
| `app.py` | Main Flask application file |
| `routes.py` | Defines application routes and handles requests |
| `models.py` | Defines the Crime database model |
| `database.py` | Handles database-related operations |
| `extensions.py` | Initializes Flask extensions |
| `config.py` | Contains application and database configuration |
| `data_loader.py` | Loads crime data into the database |
| `analysis.py` | Performs crime data analysis |
| `charts.py` | Contains functions for generating charts |
| `load_charts.py` | Handles chart generation/loading |
| `templates/` | Contains HTML pages |
| `static/` | Contains CSS and generated chart files |
| `data/` | Contains the crime dataset |
| `instance/` | Stores the SQLite database |
| `reports/` | Stores generated reports |
| `requirements.txt` | Contains required Python packages |

## 🗄️ Database

The project uses **SQLite** as the database.

The database file is stored in:

```text
instance/chicago_crime.db
```

The main database table used in the project is the **Crime** table.

The Crime table stores crime-related information from the Chicago crime dataset and is used for both record management and data analysis.

## 🔄 CRUD Operations

CRUD operations are implemented on the **Crime** table.

### Create
Adds a new crime record to the database.

### Read
Retrieves and displays existing crime records.

### Update
Modifies the details of an existing crime record.

### Delete
Removes an unwanted crime record from the database.

These operations allow crime records to be efficiently maintained and managed through the application.

## 📊 Data Analysis and Visualizations

The project performs analysis on crime records and generates different graphs to identify important patterns.

### 1. Arrest per Year

This graph shows the number of arrests recorded for different years.

It helps identify changes in arrest activity over time and allows comparison between different years.

### 2. Crime per Hour

This graph represents the number of crimes occurring during different hours of the day.

It helps identify the time periods during which crime occurrences are higher or lower.

### 3. Crime per Month vs Day of Week

This visualization analyzes crime occurrences by comparing **months** with **days of the week**.

It helps identify recurring patterns and determine which combinations of months and weekdays have higher crime activity.

### 4. Outlier Detection – Box Plot

A box plot is used to identify **outliers** in the crime data.

Outliers represent values that are significantly different from the majority of observations and may require further investigation.

## 📈 Key Analytics

The generated visualizations help analyze:

- Crime trends across different years.
- Arrest patterns over time.
- Crime occurrence by hour.
- Crime occurrence by month.
- Crime occurrence by day of the week.
- Differences in crime activity across time periods.
- Unusual or extreme observations using outlier analysis.

## 🔄 Application Workflow

```text
Chicago Crime Dataset
        ↓
    Data Loading
        ↓
      Database
        ↓
   Crime Table
        ↓
   CRUD Operations
        ↓
    Data Analysis
        ↓
   Chart Generation
        ↓
 Crime Visualizations
        ↓
    Crime Insights
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone <your-github-repository-url>
```

Navigate to the project directory:

```bash
cd Chicago-Crime-Analytics
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

For Windows:

```bash
.venv\Scripts\activate
```

### 4. Install Required Packages

```bash
pip install -r requirements.txt
```

### 5. Load the Crime Dataset

Make sure the required crime dataset is placed inside the:

```text
data/
```

folder.

Run the data loading script if required:

```bash
python data_loader.py
```

### 6. Generate Charts

Run the chart loading/generation script:

```bash
python load_charts.py
```

### 7. Run the Application

Start the Flask application:

```bash
python app.py
```

The application will run on the configured local server.

Open the displayed localhost address in a web browser.

## 📋 Requirements

The required Python packages are listed in:

```text
requirements.txt
```

Install them using:

```bash
pip install -r requirements.txt
```

## 📌 Project Features

- Crime data loading
- SQLite database storage
- Crime record management
- Create, Read, Update, and Delete operations
- Crime data analysis
- Arrest analysis by year
- Crime analysis by hour
- Month vs day-of-week analysis
- Outlier detection using box plots
- Graph generation
- Web-based interface
- Crime insights and reporting

## 🔍 Sample Insights

The generated graphs can be used to identify observations such as:

- Arrest levels vary across different years.
- Crime occurrences are not evenly distributed throughout the day.
- Certain months and days of the week may show higher crime activity.
- Box plots can reveal unusual values or potential outliers in the dataset.

These insights help provide a better understanding of crime patterns in Chicago.

## 🚀 Future Enhancements

The project can be further enhanced by adding:

- Interactive dashboards.
- Crime location mapping using geographical maps.
- Advanced search and filtering.
- Crime prediction using Machine Learning.
- User authentication and authorization.
- Real-time crime data integration.
- Downloadable analytical reports.
- More advanced statistical analysis.
- Interactive charts with filtering options.

## 🎓 Project Purpose

This project demonstrates the practical implementation of:

- **Python programming**
- **Flask web development**
- **Database management**
- **CRUD operations**
- **Data analysis**
- **Data visualization**
- **Statistical outlier detection**

It provides a complete workflow from **crime data loading and database management to analysis, visualization, and insight generation**.

## 📄 License

This project is developed for **educational and academic purposes**.
