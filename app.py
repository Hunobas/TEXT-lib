from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # 보안을 위한 시크릿 키, 실제로는 더 안전한 방법을 사용해야 합니다.

# MongoDB 연결 설정
client = MongoClient('localhost', 27017)
db = client.dbjungle
users_collection = db.users

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = users_collection.find_one({'username': username})

    if user and check_password_hash(user['password'], password):
        session['user'] = user['username']
        return redirect(url_for('dashboard'))
    else:
        return "Invalid login credentials. Please try again."
    

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # 간단한 입력 유효성 검증
    if not username or not password or not confirm_password:
        return "All fields must be filled out."

    if password != confirm_password:
        return "Passwords do not match."

    # 이미 가입된 사용자인지 확인
    existing_user = users_collection.find_one({'username': username})
    if existing_user:
        return "Username is already taken. Please choose another one."

    # 비밀번호 해싱
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    # MongoDB에 사용자 정보 저장
    new_user = {
        'username': username,
        'password': hashed_password
    }
    users_collection.insert_one(new_user)

    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return f"Welcome, {session['user']}! This is your dashboard."
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
