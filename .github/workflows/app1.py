from flask import Flask, render_template, request
import sqlite3
import pandas as pd

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('ilgi_data.db')  #
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            mood TEXT,
            workout_parts TEXT,
            feedback TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # 서버 시작 시 테이블 생성

# SQLite 데이터베이스 연결
def get_db_connection():
    conn = sqlite3.connect('dak_products_20250223_5.db')  # SQLite DB 파일 위치
    conn.row_factory = sqlite3.Row  # 결과를 딕셔너리 형태로 반환하도록 설정
    return conn

@app.route('/')
def ent():
    return render_template('entrance.html')

@app.route('/cal', methods=["GET"])
def dak_cal():
    num1 = request.args.get("num1", type=int)
    num2 = request.args.get("num2", type=int)
    
    #만약 num1 또는 num2가 없으면 None을 리턴
    if num1 is None or num2 is None:
        return render_template("calculator.html", result=None)
    
    conn = get_db_connection()
    query = """SELECT
                브랜드,
                이미지_URL AS 이미지,      
                이름,        
                가격,          
                단백질,
                칼로리,
                별점,
                CAST(가격 AS INTEGER) * ? AS 가격선호값,    
                CAST(단백질 AS FLOAT) * ? AS 단백질선호값 
            FROM products
            """
    df_prices = pd.read_sql(query, conn, params=(num1, num2))
    conn.close()
    df_prices['최적화값'] = df_prices['가격선호값'] - df_prices['단백질선호값']
    df_prices = df_prices.sort_values(by='최적화값', ascending=True) #ascending False이면 내림차
    df_prices['이미지'] = df_prices['이미지'].apply(lambda url: f'<img src="{url}" width="100">' if url else "이미지 없음")
    df_prices['번호'] = range(1, len(df_prices) + 1)
    
    df_combined = df_prices[['번호', '브랜드', '이미지', '이름', '가격', '단백질', '칼로리', '별점', '가격선호값', '단백질선호값', '최적화값']]
    combined_html = df_combined.to_html(classes="table table-bordered", index=False, escape=False)
    return render_template("calculator.html", result=combined_html)

@app.route('/ilgi')
def index():
    conn = sqlite3.connect('ilgi_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM records ORDER BY date DESC")
    records = cursor.fetchall()
    conn.close()
    return render_template('ilgi.html', records=records)


@app.route('/save', methods=['POST'])
def save_record():
    # 폼에서 데이터 가져오기
    date = request.form['date']
    mood = request.form['mood']
    workout_parts = ', '.join(request.form.getlist('workout_parts'))  # 여러 값 가져오기
    feedback = request.form['feedback']
    
    # 데이터베이스에 저장
    conn = sqlite3.connect('ilgi_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO records (date, mood, workout_parts, feedback) VALUES (?, ?, ?, ?)",
              (date, mood, workout_parts, feedback))
    conn.commit()
    conn.close()

    return '일기 저장 완료!'

@app.route('/view')
def view_records():
    conn = sqlite3.connect('ilgi_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM records")
    records = c.fetchall()
    conn.close()
    
    # HTML로 출력
    return render_template('view.html', records=records)

if __name__ == '__main__':
    app.run(debug=True)
