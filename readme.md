# 📦 Flipkart Hyperlocal Delivery Assignment System

A lightweight RESTful backend service that automates the assignment of Flipkart Quick orders to the most optimal delivery partner — in real-time, using a smart priority scoring system.

---

## 🚀 Project Overview

Flipkart Quick promises grocery and essentials delivery within **90 minutes**. As demand increases, manually assigning orders to delivery partners creates delays and inefficiencies.

This project solves that by offering a **smart assignment engine** using Flask, where:

- Orders are instantly assigned to the **best available partner**
- Assignments are made based on **rating, availability, pincode, and capacity**
- You can test all endpoints easily with a built-in Python test script

---

## 🧠 Assignment Logic (Core Rules)

When a new order is placed, the system applies the following logic:

### ✅ Filtering Criteria:

- Partner must be **AVAILABLE**
- Partner must be in the **same pincode** as the order
- Partner must have **capacity > 0**

### 📊 Priority Score Calculation:

Priority Score = (rating × 0.6) + (capacity × 0.4)

### ⚖️ Tie-Breaker:

If two partners have the same score, choose the one with the **alphabetically smaller `partnerId`**.

### 🔄 Assignment:

- Assign the order to the top-scoring eligible partner
- Update order status to **ASSIGNED**
- Reduce partner’s capacity by **1**

---

## 🧩 Data Models

### 📌 Order

| Field        | Type   | Description                           |
| ------------ | ------ | ------------------------------------- |
| orderId      | string | Unique ID (e.g., `FK-ORD-12345`)      |
| pincode      | string | 6-digit destination pincode           |
| itemsValue   | float  | Total value of order items            |
| isPlusMember | bool   | Whether the customer is a Plus member |
| status       | string | `PENDING` / `ASSIGNED` / ...          |
| assignedTo   | string | Partner ID assigned (or `null`)       |

### 👤 DeliveryPartner

| Field     | Type   | Description                                |
| --------- | ------ | ------------------------------------------ |
| partnerId | string | Unique ID (e.g., `FP-PART-007`)            |
| pincode   | string | Current location of partner                |
| rating    | float  | From 1.0 to 5.0                            |
| status    | string | `AVAILABLE` / `ON_DELIVERY` / `OFFLINE`    |
| capacity  | int    | Number of orders the partner can carry now |

---

## 🔌 API Endpoints

### `POST /orders`

Create a new order  
**Request JSON:**

```json
{
  "orderId": "FK-ORD-001",
  "pincode": "560001",
  "itemsValue": 750.00,
  "isPlusMember": true
}

POST /assign
Assign the best partner to a pending order
Request JSON:
{
  "orderId": "FK-ORD-001"
}
GET /orders/<orderId>
Fetch details of a specific order (including partner info if assigned)

GET /partners
List all delivery partners (for testing/debug)

POST /partners
Add a new delivery partner
Request JSON:
{
  "partnerId": "FP-PART-010",
  "pincode": "560001",
  "rating": 4.5,
  "status": "AVAILABLE",
  "capacity": 3
}
```

🛠️ Setup Instructions

1. Clone the repo
git clone https://github.com/shubhangam-singh
flipkart-delivery-system.git
cd flipkart-delivery-system

2. Create and activate virtual environment
python -m venv venv
for Windows
venv\Scripts\activate
for macOS/Linux
source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Run the server
python main.py

🧪 Testing the API
Run the included test script to simulate a complete workflow:
python test_api.py

This will:

. Ping the health endpoint
. Create an order
. Assign a partner
. Fetch order and partner details

🧼 Sample Output

🎯 Running Complete Test Scenario
🔍 Testing Health Check...
📦 Testing Create Order...
🚚 Testing Assign Order...
📋 Testing Get Order...
✅ All tests completed successfully!


📂 Folder Structure
flipkart-delivery-system/
├── main.py           # Flask backend logic
├── test_api.py       # Automated API test script
├── requirements.txt  # Python package dependencies
├── readme.md         # Project overview and documentation
└── venv/             # Virtual environment (excluded from Git)


🌟 Future Enhancements
. Switch to SQLite or PostgreSQL for persistent storage
. Add authentication for admin endpoints
. Dockerize for deployment
. Add frontend dashboard for partner/order tracking
. Extend partner logic (geo-distance, availability slots, etc.)

👨‍💻 Author
Made with ❤️ by Shubhangam
Feel free to ⭐ this repo or raise an issue/PR if you'd like to contribute!

📝 License
This project is open-source and free to use under the MIT License.

---
```
