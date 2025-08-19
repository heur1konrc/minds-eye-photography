from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Mind's Eye Photography v2.0 is live!"

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
