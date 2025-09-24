from flask import Flask, render_template, request, jsonify
from waitress import serve
from advanced_memory_manager import MemoryManager

app = Flask(__name__, template_folder='templates', static_folder='static')
mm = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/init', methods=['POST'])
def init_memory():
    global mm
    total_size = request.json.get('total_size', 1000)
    mm = MemoryManager(total_size)
    return jsonify(mm.to_dict())

@app.route('/allocate', methods=['POST'])
def allocate():
    if not mm:
        return jsonify({"error": "Memory not initialized"}), 400
    size = request.json.get('size', 100)
    strategy = request.json.get('strategy', 'best')
    mm.allocate(size, strategy)
    return jsonify(mm.to_dict())

@app.route('/deallocate', methods=['POST'])
def deallocate():
    if not mm:
        return jsonify({"error": "Memory not initialized"}), 400
    block_id = request.json.get('block_id')
    if block_id is None:
        return jsonify({"error": "Block ID is required"}), 400
    mm.deallocate(block_id)
    return jsonify(mm.to_dict())

@app.route('/deallocate_multiple', methods=['POST'])
def deallocate_multiple():
    if not mm:
        return jsonify({"error": "Memory not initialized"}), 400
    block_ids = request.json.get('block_ids')
    if not block_ids or not isinstance(block_ids, list):
        return jsonify({"error": "A list of block IDs is required"}), 400
    
    for block_id in block_ids:
        mm.deallocate(block_id)
    
    return jsonify(mm.to_dict())

if __name__ == '__main__':
    print("Starting server on http://localhost:5002")
    serve(app, host='0.0.0.0', port=5002)