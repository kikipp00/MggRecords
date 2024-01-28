from flask import Flask, render_template, request, send_from_directory, redirect, url_for, send_file, current_app
import os
import mgg

# todo: timestamp
# todo: count
# if access from multiple user simultaneously, they all use same db

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
    return redirect(url_for('result',
                            userid=userid,
                            category='Want'), code=307)


@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        category = request.values.get('category')
        conn = mgg.create_connection()
        cur = conn.cursor()
        with conn:
            cur.execute(f"SELECT * FROM {category} WHERE userid={request.values.get('userid')}")
            rows = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
        return render_template('result.html',
                               userid=request.values.get('userid'),
                               column_names=column_names,
                               rows=rows,
                               category=category)
    if request.method == 'GET':
        redirect(url_for('/'))


# serves client csv of current category
# deletes csv immediately from server
@app.route('/download/<category>', methods=['POST', 'GET'])  # why url no change??
def download_csv(category):
    file_path = mgg.to_csv(category)

    def stream_and_remove_file():
        with open(file_path) as f:
            yield from f
        os.remove(file_path)

    return current_app.response_class(
        stream_and_remove_file(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment', 'filename': file_path}
    )


if __name__ == '__main__':
    app.run(debug=True)  # auto reload
    #app.run(host="0.0.0.0")
