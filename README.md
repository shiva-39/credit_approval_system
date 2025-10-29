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

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "monthly_income": 50000,
  "phone_number": 9876543210
}
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

### 2. Check Eligibility
`POST /check-eligibility`

**Request:**
```json
{
  "customer_id": 1,
  "loan_amount": 500000,
  "interest_rate": 10.0,
  "tenure": 24
}
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

### 3. Create Loan
`POST /create-loan`

**Request:**
```json
{
  "customer_id": 1,
  "loan_amount": 500000,
  "interest_rate": 10.0,
  "tenure": 24
}
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

### 4. View Loan
`GET /view-loan/<loan_id>`

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

### 5. View Customer Loans
`GET /view-loans/<customer_id>`

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
