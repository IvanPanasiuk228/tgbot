from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Test Flask app works!"

@app.route("/test")
def test():
    return "Test endpoint works!"

if __name__ == "__main__":
    print("=== ТЕСТОВИЙ FLASK ЗАПУСКАЄТЬСЯ ===")
    app.run(host="0.0.0.0", port=10001, debug=True) 