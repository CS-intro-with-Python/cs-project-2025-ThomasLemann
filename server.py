from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', "POST"])
def hello():
    return render_template('main.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    return render_template('login.html', email=email, password=password)

@app.route('/note', methods=['GET', 'POST'])
def note():
    return render_template('note.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)