from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "ESP32 is connected!"

@app.route('/send_data', methods=['POST'])
def receive_data():
    data = request.get_json()  # get JSON data sent from ESP32
    print(f"Received data: {data}")
    return jsonify({"status": "Data received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Make the server accessible on all network interfaces
