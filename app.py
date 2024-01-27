from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import sqlite3
import os
import mgg

app = Flask(__name__)  # create flask app w/ name "app"


# set icon for tabs
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')


@app.route('/')
def form():
    return render_template('form.html')


@app.route('/', methods=['POST'])
def data():
    userid = request.form['userid']
    mgg.init_db()

    if 'want' in request.form:
        mgg.scan_category(1, userid)
    if 'reading' in request.form:
        mgg.scan_category(2, userid)
    if 'read' in request.form:
        mgg.scan_category(3, userid)
    return redirect(url_for('result', userid=userid, category='Want'), code=307)


@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'GET':
        return f"The URL /result is accessed directly. Try going to '/result' to submit form"
    if request.method == 'POST':
        conn = mgg.create_connection(mgg.database)
        with conn:
            rows = conn.execute('SELECT * FROM Reading').fetchall()
            column_names = [fields[1] for fields in conn.execute("PRAGMA table_info(Reading)").fetchall()]
        return render_template('result.html', rows=rows, column_names=column_names)


if __name__ == '__main__':
    app.run(debug=True)  # auto reload
