import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_create_order():
    """Test creating a new order"""
    print("📦 Testing Create Order...")
    order_data = {
        "orderId": "FK-ORD-TEST-001",
        "pincode": "560001",
        "itemsValue": 1250.00,
        "isPlusMember": True
    }
    
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_assign_order():
    """Test assigning an order"""
    print("🚚 Testing Assign Order...")
    assign_data = {
        "orderId": "FK-ORD-TEST-001"
    }
    
    response = requests.post(f"{BASE_URL}/assign", json=assign_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_get_order():
    """Test getting order details"""
    print("📋 Testing Get Order...")
    response = requests.get(f"{BASE_URL}/orders/FK-ORD-TEST-001")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_get_partners():
    """Test getting all partners"""
    print("👥 Testing Get All Partners...")
    response = requests.get(f"{BASE_URL}/partners")
    print(f"Status: {response.status_code}")
    partners = response.json()
    print(f"Total Partners: {len(partners)}")
    for partner in partners[:3]:  # Show first 3 partners
        print(f"  {partner['partnerId']}: {partner['pincode']} (Rating: {partner['rating']})")
    print("-" * 50)

def run_complete_test():
    """Run a complete test scenario"""
    print("🎯 Running Complete Test Scenario")
    print("=" * 50)
    
    try:
        # Test 1: Health check
        test_health()
        
        # Test 2: Get available partners
        test_get_partners()
        
        # Test 3: Create order
        test_create_order()
        
        # Test 4: Assign order
        test_assign_order()
        
        # Test 5: Get order details
        test_get_order()
        
        print("✅ All tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("Make sure the Flask server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_complete_test()