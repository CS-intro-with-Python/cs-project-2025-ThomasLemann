from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({'message': 'Hello, World!'})

@app.route('/user/<string:username>')
def user(username):
    return jsonify({'username': f"Hello, {username}!"})

@app.route('/search')
def search():
    query = request.args.get('q')
    number_of_characters = int(request.args.get('length', 1))
    return jsonify({"query": query, "length": number_of_characters})

if __name__ == '__main__':
    app.run(port=8080)