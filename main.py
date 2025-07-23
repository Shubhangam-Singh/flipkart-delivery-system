from flask import Flask, request, jsonify
from datetime import datetime
import json
from typing import List, Dict, Optional

app = Flask(__name__)

# In-memory data stores
orders = []
delivery_partners = []

class Order:
    def __init__(self, order_id: str, pincode: str, items_value: float, is_plus_member: bool):
        self.order_id = order_id
        self.pincode = pincode
        self.items_value = items_value
        self.is_plus_member = is_plus_member
        self.status = "PENDING"
        self.assigned_to = None
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "orderId": self.order_id,
            "pincode": self.pincode,
            "itemsValue": self.items_value,
            "isPlusMember": self.is_plus_member,
            "status": self.status,
            "assignedTo": self.assigned_to,
            "createdAt": self.created_at
        }

class DeliveryPartner:
    def __init__(self, partner_id: str, pincode: str, rating: float, status: str, capacity: int):
        self.partner_id = partner_id
        self.pincode = pincode
        self.rating = rating
        self.status = status
        self.capacity = capacity
    
    def to_dict(self):
        return {
            "partnerId": self.partner_id,
            "pincode": self.pincode,
            "rating": self.rating,
            "status": self.status,
            "capacity": self.capacity
        }
    
    def calculate_priority_score(self):
        """Calculate priority score using weighted formula"""
        return (self.rating * 0.6) + (self.capacity * 0.4)

# Initialize sample delivery partners
def initialize_sample_data():
    global delivery_partners
    
    sample_partners = [
        DeliveryPartner("FP-PART-001", "560001", 4.5, "AVAILABLE", 3),
        DeliveryPartner("FP-PART-002", "560001", 4.2, "AVAILABLE", 2),
        DeliveryPartner("FP-PART-003", "560002", 4.8, "AVAILABLE", 1),
        DeliveryPartner("FP-PART-004", "560001", 4.5, "AVAILABLE", 3),
        DeliveryPartner("FP-PART-005", "560003", 3.9, "AVAILABLE", 4),
        DeliveryPartner("FP-PART-006", "560001", 4.7, "ON_DELIVERY", 2),
        DeliveryPartner("FP-PART-007", "560002", 4.3, "AVAILABLE", 0),
        DeliveryPartner("FP-PART-008", "560001", 4.1, "OFFLINE", 3),
    ]
    
    delivery_partners.extend(sample_partners)

# Helper functions
def find_order_by_id(order_id: str) -> Optional[Order]:
    """Find order by ID"""
    for order in orders:
        if order.order_id == order_id:
            return order
    return None

def find_partner_by_id(partner_id: str) -> Optional[DeliveryPartner]:
    """Find delivery partner by ID"""
    for partner in delivery_partners:
        if partner.partner_id == partner_id:
            return partner
    return None

def get_eligible_partners(pincode: str) -> List[DeliveryPartner]:
    """Get eligible delivery partners based on filtering criteria"""
    eligible_partners = []
    
    for partner in delivery_partners:
        # Filtering criteria
        if (partner.status == "AVAILABLE" and 
            partner.pincode == pincode and 
            partner.capacity > 0):
            eligible_partners.append(partner)
    
    return eligible_partners

def select_best_partner(eligible_partners: List[DeliveryPartner]) -> Optional[DeliveryPartner]:
    """Select the best partner based on priority score and tie-breaker rules"""
    if not eligible_partners:
        return None
    
    # Calculate priority scores and sort
    partner_scores = []
    for partner in eligible_partners:
        score = partner.calculate_priority_score()
        partner_scores.append((partner, score))
    
    # Sort by priority score (descending) and then by partner ID (ascending) for tie-breaking
    partner_scores.sort(key=lambda x: (-x[1], x[0].partner_id))
    
    return partner_scores[0][0]

# API Endpoints

@app.route('/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    try:
        # --- MANUAL PARSING FIX ---
        raw_string = request.data.decode('utf-8')
        clean_string = raw_string.strip('{}')
        data = {}
        pairs = clean_string.split(',')
        for pair in pairs:
            key, value = pair.split(':', 1)
            value = value.strip().strip("'\"")
            data[key.strip()] = value
        # --- END OF FIX ---

        # Validate required fields
        required_fields = ['orderId', 'pincode', 'itemsValue']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Validate data types and values
        order_id = data['orderId']
        pincode = str(data['pincode'])
        items_value = float(data['itemsValue'])
        is_plus_member = str(data.get('isPlusMember', 'false')).lower() == 'true'

        if find_order_by_id(order_id):
            return jsonify({"error": "Order ID already exists"}), 400

        if len(pincode) != 6 or not pincode.isdigit():
            return jsonify({"error": "Pincode must be a 6-digit number"}), 400

        new_order = Order(order_id, pincode, items_value, is_plus_member)
        orders.append(new_order)

        return jsonify({
            "message": "Order created successfully",
            "order": new_order.to_dict()
        }), 201

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
@app.route('/assign', methods=['POST'])
def assign_order():
    """Assign an order to the best available delivery partner"""
    try:
        # --- MANUAL PARSING FIX ---
        raw_string = request.data.decode('utf-8')
        clean_string = raw_string.strip('{}')
        data = {}
        pairs = clean_string.split(',')
        for pair in pairs:
            key, value = pair.split(':', 1)
            value = value.strip().strip("'\"")
            data[key.strip()] = value
        # --- END OF FIX ---

        if 'orderId' not in data:
            return jsonify({"error": "Missing required field: orderId"}), 400

        order_id = data['orderId']
        order = find_order_by_id(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        if order.status != "PENDING":
            return jsonify({"error": f"Order cannot be assigned. Current status: {order.status}"}), 400

        eligible_partners = get_eligible_partners(order.pincode)

        if not eligible_partners:
            return jsonify({
                "message": "No eligible delivery partners available for this order",
                "order": order.to_dict(),
                "assignedPartner": None
            }), 200

        best_partner = select_best_partner(eligible_partners)

        if not best_partner:
            return jsonify({
                "message": "No suitable delivery partner found",
                "order": order.to_dict(),
                "assignedPartner": None
            }), 200

        order.status = "ASSIGNED"
        order.assigned_to = best_partner.partner_id
        best_partner.capacity -= 1

        return jsonify({
            "message": "Order assigned successfully",
            "order": order.to_dict(),
            "assignedPartner": best_partner.to_dict(),
        }), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id: str):
    """Get order details by ID"""
    try:
        order = find_order_by_id(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        response_data = order.to_dict()
        
        # If order is assigned, include partner details
        if order.assigned_to:
            partner = find_partner_by_id(order.assigned_to)
            if partner:
                response_data["assignedPartnerDetails"] = partner.to_dict()
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# Additional utility endpoints for testing and management

@app.route('/partners', methods=['GET'])
def get_all_partners():
    """Get all delivery partners (for testing purposes)"""
    return jsonify([partner.to_dict() for partner in delivery_partners]), 200

@app.route('/partners/<partner_id>', methods=['GET'])
def get_partner(partner_id: str):
    """Get delivery partner details by ID"""
    partner = find_partner_by_id(partner_id)
    if not partner:
        return jsonify({"error": "Partner not found"}), 404
    
    return jsonify(partner.to_dict()), 200

@app.route('/partners', methods=['POST'])
def add_partner():
    """Add a new delivery partner"""
    try:
        data = request.get_json()
        
        required_fields = ['partnerId', 'pincode', 'rating', 'status', 'capacity']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        partner_id = data['partnerId']
        pincode = str(data['pincode'])
        rating = float(data['rating'])
        status = data['status']
        capacity = int(data['capacity'])
        
        # Validate data
        if find_partner_by_id(partner_id):
            return jsonify({"error": "Partner ID already exists"}), 400
        
        if len(pincode) != 6 or not pincode.isdigit():
            return jsonify({"error": "Pincode must be a 6-digit number"}), 400
        
        if not (1.0 <= rating <= 5.0):
            return jsonify({"error": "Rating must be between 1.0 and 5.0"}), 400
        
        if status not in ["AVAILABLE", "ON_DELIVERY", "OFFLINE"]:
            return jsonify({"error": "Invalid status"}), 400
        
        if capacity < 0:
            return jsonify({"error": "Capacity must be non-negative"}), 400
        
        new_partner = DeliveryPartner(partner_id, pincode, rating, status, capacity)
        delivery_partners.append(new_partner)
        
        return jsonify({
            "message": "Partner added successfully",
            "partner": new_partner.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/orders', methods=['GET'])
def get_all_orders():
    """Get all orders (for testing purposes)"""
    return jsonify([order.to_dict() for order in orders]), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "totalOrders": len(orders),
        "totalPartners": len(delivery_partners)
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

if __name__ == '__main__':
    # Initialize sample data
    initialize_sample_data()
    
    print("🚀 Flipkart Hyperlocal Delivery Assignment System")
    print("📍 Server starting on http://localhost:5000")
    print("📋 Sample delivery partners loaded")
    print("🔧 Ready to process orders!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)