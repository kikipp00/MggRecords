from flask import Flask, render_template, request
import sqlite3
import mgg

app = Flask(__name__)  # create flask app w/ name "app"


"""@app.route('/other')
def index():
    conn = mgg.create_connection(mgg.database)
    posts = conn.execute('SELECT * FROM Want').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)"""


@app.route('/')
def form():
    return render_template('form.html')


@app.route('/data', methods=['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        form_data = request.form
        mgg.init_db()

        # todo: loading page
        if 'want' in request.form:
            mgg.scan_category(1, form_data['userid'])
        if 'reading' in request.form:
            mgg.scan_category(2, form_data['userid'])
        if 'read' in request.form:
            mgg.scan_category(3, form_data['userid'])

        conn = mgg.create_connection(mgg.database)
        with conn:
            rows = conn.execute('SELECT * FROM Reading').fetchall()

        return render_template('result.html', rows=rows)


if __name__ == '__main__':
    app.run()
