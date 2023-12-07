from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

def calculate_delivery_fee(cart_value, delivery_distance, number_of_items, delivery_time):
    # Check if it's Friday rush (3 - 7 PM UTC)
    is_friday_rush = False
    try:
        delivery_time = datetime.strptime(delivery_time, "%Y-%m-%dT%H:%M:%SZ")
        if delivery_time.weekday() == 4 and 15 <= delivery_time.hour < 19:
            is_friday_rush = True
    except ValueError:
        # Handle invalid datetime format
        return None

    # Calculate delivery fee
    base_fee = 2
    distance_fee = min(15, base_fee + (1 + (delivery_distance - 1000) // 500))
    cart_value_surcharge = max(0, cart_value - 10)
    item_surcharge = 0.5 * max(0, number_of_items - 4)
    bulk_fee = 1.2 if number_of_items > 12 else 1
    total_fee = distance_fee + cart_value_surcharge + item_surcharge + bulk_fee

    # Apply Friday rush multiplier
    if is_friday_rush:
        total_fee *= 1.2

    return min(15, round(total_fee, 2))

@app.route('/deliveryFee', methods=['POST'])
def calculate_delivery_fee_endpoint():
    try:
        data = request.get_json()
        cart_value = data.get('cart_value')
        delivery_distance = data.get('delivery_distance')
        number_of_items = data.get('number_of_items')
        delivery_time = data.get('time')

        if cart_value is None or delivery_distance is None or number_of_items is None or delivery_time is None:
            raise ValueError("Missing required parameters")

        delivery_fee = calculate_delivery_fee(cart_value, delivery_distance, number_of_items, delivery_time)

        if delivery_fee is None:
            raise ValueError("Invalid datetime format")

        response = {"delivery_fee": int(delivery_fee * 100)}  # Convert to cents for precision
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=8080)
