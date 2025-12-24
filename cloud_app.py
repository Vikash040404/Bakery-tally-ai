from flask import Flask, render_template, request, jsonify
import uuid

app = Flask(__name__)

# --- THE TEMPORARY DATABASE ---
# Stores bills until the laptop downloads them
bill_queue = []

@app.route('/')
def index():
    return render_template('index.html')

# --- API: RECEIVE ORDER FROM PHONE/TABLET ---
@app.route('/api/submit-bill', methods=['POST'])
def submit_bill():
    data = request.json
    
    # Create a unique ID
    bill_id = str(uuid.uuid4())
    
    new_order = {
        "id": bill_id,
        "customer": data.get('customer', 'Cash'),
        "items": data.get('items', []),
        "status": "pending"
    }
    
    bill_queue.append(new_order)
    print(f"✅ New Order Received: {bill_id} for {new_order['customer']}")
    
    return jsonify({"status": "success", "message": "Sent to Shop Laptop!"})

# --- API: LAPTOP ASKS 'ANY NEW BILLS?' ---
@app.route('/api/get-pending-bills', methods=['GET'])
def get_pending():
    return jsonify({"bills": bill_queue})

# --- API: LAPTOP SAYS 'DONE' ---
@app.route('/api/mark-complete', methods=['POST'])
def mark_complete():
    data = request.json
    completed_id = data.get('bill_id')
    
    global bill_queue
    # Remove the completed bill from the list
    bill_queue = [b for b in bill_queue if b['id'] != completed_id]
    
    return jsonify({"status": "success"})
 
if __name__ == '__main__':
    app.run(debug=True, port=5000)
 
 
