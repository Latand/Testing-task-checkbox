# Test Task

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Docker**: Download and install Docker [here](https://docs.docker.com/get-docker/).
- **Docker Compose**: Download and install Docker Compose [here](https://docs.docker.com/compose/install/).
- **Make**: Ensure you have `Make` compatible tool installed for running `Makefiles`. You can install `Make` on Linux by running `sudo apt-get install make`.

## Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/Latand/Testing-task-checkbox
cd Testing-task-checkbox
```


## Environment Setup

Copy the `.env.dist` file to `.env` and update the environment variables with your specific values:

```bash
cp .env.dist .env
```

Edit the `.env` file and add the following environment variables:

```
POSTGRES_USER=someusername
POSTGRES_PASSWORD=postgres_pass12345
POSTGRES_DB=bot
DB_HOST=pg_database

SECRET_KEY=your_secret_key
```

## Running the Project

To build and run the project, execute:

```bash
make build
```

## Database Migration

Once the project build is complete, run the following command to migrate the database:

```bash
make migrate
```

## Testing the API

At this point, the API should be up and running and can be tested via the endpoint URLs provided in [API documentation](http://localhost:8000/docs).

## Running Tests

To run tests, you first need to install the necessary dependencies:

```bash
make install
```

Then, you can execute the tests with:

```bash
make test
```


## API Documentation

The API documentation can be accessed at [http://localhost:8000/docs](http://localhost:8000/docs).
Here you can find the list of available endpoints and their respective request and response schemas.


## Authentication

### Signup

- Endpoint: `/signup`
- Method: POST
- Request Body:
  - `username` (string): Username for the new user.
  - `full_name` (string): Full name of the user.
  - `password` (string): Password for the user account.
- Response:
  - `access_token` (string): Access token for authentication.
  - `token_type` (string): Type of the token (e.g., "bearer").
  - `expires_in` (integer): Expiration time of the access token in seconds.

### Login

- Endpoint: `/token`
- Method: GET
- Query Parameters:
  - `username` (string): Username for authentication.
  - `password` (string): Password for authentication.
- Response:
  - `access_token` (string): Access token for authentication.
  - `token_type` (string): Type of the token (e.g., "bearer").
  - `expires_in` (integer): Expiration time of the access token in seconds.

## Receipts

### Create Receipt

- Endpoint: `/receipts/`
- Method: POST
- Request Body:
  - `products` (array of objects):
    - `name` (string): Name of the product.
    - `price` (decimal): Price of the product.
    - `quantity` (decimal): Quantity of the product.
  - `payment` (object):
    - `type` (string): Type of payment (e.g., "cash", "card"), lowercase.
    - `amount` (decimal): Payment amount.
  - `comment` (string, optional): Additional comment for the receipt.
- Response:
  - `receipt_id` (integer): ID of the created receipt.
  - `products` (array of objects):
    - `name` (string): Name of the product.
    - `price` (decimal): Price of the product.
    - `quantity` (decimal): Quantity of the product.
    - `total` (decimal): Total price of the product.
  - `payment` (object):
    - `type` (string): Type of payment.
    - `amount` (decimal): Payment amount.
  - `comment` (string, optional): Additional comment for the receipt.
  - `total` (decimal): Total amount of the receipt.
  - `rest` (decimal): Remaining amount after payment.
  - `created_at` (string): Timestamp of receipt creation.

### Get Receipts

- Endpoint: `/receipts/`
- Method: GET
- Query Parameters:
  - `start_date` (datetime, optional): Start date filter for receipts.
  - `end_date` (datetime, optional): End date filter for receipts.
  - `min_total` (decimal, optional): Minimum total amount filter for receipts.
  - `max_total` (decimal, optional): Maximum total amount filter for receipts.
  - `payment_type` (string, optional): Payment type filter for receipts.
  - `limit` (integer, default: 10): Maximum number of receipts to retrieve.
  - `offset` (integer, default: 0): Offset for pagination.
- Response:
  - Array of receipt objects (same structure as in the create receipt response).

### Get Receipt by ID

- Endpoint: `/receipts/{receipt_id}`
- Method: GET
- Path Parameters:
  - `receipt_id` (integer): ID of the receipt to retrieve.
- Response:
  - Receipt object (same structure as in the create receipt response).

### Show Receipt by ID

- Endpoint: `/receipts/show/{receipt_id}/`
- Method: GET
- Path Parameters:
  - `receipt_id` (integer): ID of the receipt to show.
- Query Parameters:
  - `max_characters` (integer, default: 30): Maximum number of characters per line in the receipt text.
- Response:
  - Receipt text (plain text format).

