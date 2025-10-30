# Credit Approval System

Backend internship assignment - A Django-based credit approval system that processes loan applications based on credit scoring.

## Technology Stack

- Django 4.2.7
- Django Rest Framework 3.14.0
- PostgreSQL 15
- Celery 5.3.4 with Redis
- Docker & Docker Compose

## Setup and Run

### Prerequisites
- Docker Desktop installed

### Running the Application

1. **Start all services:**
   ```bash
   docker-compose up --build
   ```

2. **In a new terminal, create migrations and ingest data:**
   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py ingest_data
   ```

3. **Application will be available at:** http://localhost:8000

## API Endpoints

### 1. Register Customer
`POST /register`

**PowerShell Command:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/register" -Method POST -ContentType "application/json" -Body '{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "monthly_income": 50000,
  "phone_number": 9876543210
}'
```

**curl Command:**
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "monthly_income": 50000,
    "phone_number": 9876543210
  }'
```

**Response:**
```json
{
  "customer_id": 1,
  "name": "John Doe",
  "age": 30,
  "monthly_income": 50000,
  "approved_limit": 1800000,
  "phone_number": 9876543210
}
```

---

### 2. Check Eligibility
`POST /check-eligibility`

**PowerShell Command:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/check-eligibility" -Method POST -ContentType "application/json" -Body '{
  "customer_id": 1,
  "loan_amount": 500000,
  "interest_rate": 10.0,
  "tenure": 24
}'
```

**curl Command:**
```bash
curl -X POST http://localhost:8000/check-eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "loan_amount": 500000,
    "interest_rate": 10.0,
    "tenure": 24
  }'
```

**Response:**
```json
{
  "customer_id": 1,
  "approval": true,
  "interest_rate": 10.0,
  "corrected_interest_rate": 10.0,
  "tenure": 24,
  "monthly_installment": 23018.68
}
```

---

### 3. Create Loan
`POST /create-loan`

**PowerShell Command:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/create-loan" -Method POST -ContentType "application/json" -Body '{
  "customer_id": 1,
  "loan_amount": 500000,
  "interest_rate": 10.0,
  "tenure": 24
}'
```

**curl Command:**
```bash
curl -X POST http://localhost:8000/create-loan \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "loan_amount": 500000,
    "interest_rate": 10.0,
    "tenure": 24
  }'
```

**Response:**
```json
{
  "loan_id": 1,
  "customer_id": 1,
  "loan_approved": true,
  "message": "Loan approved",
  "monthly_installment": 23018.68
}
```

---

### 4. View Loan
`GET /view-loan/<loan_id>`

**PowerShell Command:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/view-loan/1" -Method GET
```

**curl Command:**
```bash
curl http://localhost:8000/view-loan/1
```

**Response:**
```json
{
  "loan_id": 1,
  "customer": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": 9876543210,
    "age": 30
  },
  "loan_amount": 500000,
  "interest_rate": 10.0,
  "monthly_installment": 23018.68,
  "tenure": 24
}
```

---

### 5. View Customer Loans
`GET /view-loans/<customer_id>`

**PowerShell Command:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/view-loans/1" -Method GET
```

**curl Command:**
```bash
curl http://localhost:8000/view-loans/1
```

**Response:**
```json
[
  {
    "loan_id": 1,
    "loan_amount": 500000,
    "interest_rate": 10.0,
    "monthly_installment": 23018.68,
    "repayments_left": 24
  }
]
```

## Data Ingestion

The system uses background workers (Celery) to ingest data from provided Excel files:
- `customer_data.xlsx`
- `loan_data.xlsx`

Run the ingestion command after starting the application:
```bash
docker-compose exec web python manage.py ingest_data
```

## Running Tests

The project includes comprehensive unit tests covering credit scoring, EMI calculations, and API endpoints.

**Run all tests:**
```bash
docker-compose exec web python manage.py test loans.tests
```

**Test Coverage:**
- Credit score calculation with 5 components
- Monthly installment (EMI) calculation using compound interest
- Loan eligibility logic with approval rules
- Customer and Loan model functionality

## Credit Scoring

Credit scores (0-100) are calculated based on:
1. Past loans paid on time (30%)
2. Number of loans taken (20%)
3. Loan activity in current year (20%)
4. Loan approved volume (20%)
5. Current debt check (10%)

**Approval Rules:**
- Credit Score > 50: Approve
- 30 < Score ≤ 50: Approve with interest ≥ 12%
- 10 < Score ≤ 30: Approve with interest ≥ 16%
- Score ≤ 10: Reject
- Total EMIs > 50% of salary: Reject

## Project Structure

```
credit_approval_system/
├── customers/              # Customer app with registration
├── loans/                  # Loan processing and credit scoring
├── customer_data.xlsx      # Provided customer data
├── loan_data.xlsx          # Provided loan data
├── docker-compose.yml      # Docker services configuration
├── Dockerfile              # Application container
└── requirements.txt        # Python dependencies
```

## Video Demo Recording Guide

Follow these steps to record a comprehensive demo video for submission:

### Prerequisites for Recording
- Screen recording software (OBS Studio, Loom, or Windows Game Bar)
- Postman or similar API testing tool
- Ensure Docker Desktop is running

### Recording Steps & Commands

#### 1. **Start Application (Show in Terminal)**
```bash
# Clean start - stop any running containers
docker-compose down

# Build and start all services
docker-compose up --build
```
**What to show:** Wait until all 5 services are running (web, db, redis, celery, celery-beat)

#### 2. **Database Setup & Data Ingestion (New Terminal)**
```bash
# Open a new terminal window

# Run migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Ingest data from Excel files
docker-compose exec web python manage.py ingest_data
```
**What to show:** Successful ingestion message showing 50 customers and 62 loans loaded

#### 3. **Test API Endpoint 1: Register Customer**
**Method:** POST  
**URL:** `http://localhost:8000/register`  
**Body (JSON):**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "monthly_income": 50000,
  "phone_number": 9876543210
}
```
**What to show:** Successful registration with `customer_id` and `approved_limit` in response

#### 4. **Test API Endpoint 2: Check Loan Eligibility**
**Method:** POST  
**URL:** `http://localhost:8000/check-eligibility`  
**Body (JSON):**
```json
{
  "customer_id": 1,
  "loan_amount": 500000,
  "interest_rate": 10.0,
  "tenure": 24
}
```
**What to show:** Response with `approval`, `corrected_interest_rate`, and `monthly_installment`

#### 5. **Test API Endpoint 3: Create Loan**
**Method:** POST  
**URL:** `http://localhost:8000/create-loan`  
**Body (JSON):**
```json
{
  "customer_id": 1,
  "loan_amount": 500000,
  "interest_rate": 10.0,
  "tenure": 24
}
```
**What to show:** Successful loan creation with `loan_id` and approval message

#### 6. **Test API Endpoint 4: View Specific Loan**
**Method:** GET  
**URL:** `http://localhost:8000/view-loan/1`  
**What to show:** Loan details with nested customer information

#### 7. **Test API Endpoint 5: View Customer's All Loans**
**Method:** GET  
**URL:** `http://localhost:8000/view-loans/1`  
**What to show:** Array of loans with `repayments_left` field

#### 8. **Run Unit Tests**
```bash
# Run all unit tests
docker-compose exec web python manage.py test loans.tests -v 2
```
**What to show:** All 11 tests passing successfully

#### 9. **Verify Data in Database (Optional but Impressive)**
```bash
# Access PostgreSQL database
docker-compose exec db psql -U credit_user -d credit_approval_db

# Show customers
SELECT customer_id, first_name, last_name, approved_limit FROM customers_customer LIMIT 5;

# Show loans
SELECT loan_id, customer_id, loan_amount, interest_rate FROM loans_loan LIMIT 5;

# Exit
\q
```

### Video Recording Tips
- **Duration:** Keep it between 5-10 minutes
- **Voice Over:** Explain what you're doing at each step
- **Show Clearly:** Make sure terminal output and API responses are visible
- **Highlight Key Features:**
  - Credit score calculation
  - Interest rate correction
  - EMI calculation
  - All 11 tests passing
- **Upload:** Upload to YouTube (unlisted) or Google Drive with public access

### After Recording
1. Upload video to YouTube/Google Drive
2. Get the shareable link
3. Update `SUBMISSION_TEMPLATE.md` with the video link
4. Create Word document and submit to: **anoosha@alemeno.com**
