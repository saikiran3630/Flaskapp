import sqlite3

from flask import Flask, request, g, render_template, send_file

DATABASE = '/var/www/html/flaskapp/example.db'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_to_database():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def execute_query(query, args=()):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows

def commit():
    get_db().commit()

@app.route("/")
def hello():
    execute_query("DROP TABLE IF EXISTS users")
    execute_query("CREATE TABLE users (Username text,Password text,firstname text,lastname text,email text,count integer)")
    return render_template('index.html')

@app.route('/login', methods =['POST', 'GET'])
def login():
    message = ''
    if request.method == 'POST' and str(request.form['username']) !="" and str(request.form['password']) != "":
        username = str(request.form['username'])
        password = str(request.form['password'])
        result = execute_query("""SELECT firstname,lastname,email,count  FROM users WHERE Username  = (?) AND Password = (?)""", (username, password ))
        if result:
            for row in result:
                return responsePage(row[0], row[1], row[2], row[3])
        else:
            message = 'Invalid Credentials !'
    elif request.method == 'POST':
        message = 'Please enter Credentials'
    return render_template('index.html', message = message)

@app.route('/registration', methods =['GET', 'POST'])
def registration():
    message = ''
    if request.method == 'POST' and str(request.form['username']) !="" and str(request.form['password']) !="" and str(request.form['firstname']) !="" and str(request.form['lastname']) !="" and str(request.form['email']) !="":
        username = str(request.form['username'])
        password = str(request.form['password'])
        firstname = str(request.form['firstname'])
        lastname = str(request.form['lastname'])
        email = str(request.form['email'])
        uploaded_file = request.files['textfile']
        if not uploaded_file:
            filename = null
            word_count = null
        else :
            filename = uploaded_file.filename
            word_count = getNumberOfWords(uploaded_file)
        result = execute_query("""SELECT *  FROM users WHERE Username  = (?)""", (username, ))
        if result:
            message = 'User has already registered!'
        else:
            result1 = execute_query("""INSERT INTO users (username, password, firstname, lastname, email, count) values (?, ?, ?, ?, ?, ? )""", (username, password, firstname, lastname, email, word_count, ))
            commit()
            result2 = execute_query("""SELECT firstname,lastname,email,count  FROM users WHERE Username  = (?) AND Password = (?)""", (username, password ))
            if result2:
                for row in result2:
                    return responsePage(row[0], row[1], row[2], row[3])
    elif request.method == 'POST':
        message = 'Some of the fields are missing!'
    return render_template('registration.html', message = message)

@app.route("/download")
def download():
    path = "Limerick.txt"
    return send_file(path, as_attachment=True)

def getNumberOfWords(file):
    data = file.read()
    words = data.split()
    return str(len(words))

response_page_css = """
<style>
.response-container {
    max-width: 600px;
    margin: 20px auto;
    padding: 20px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.response-container h2 {
    text-align: center;
    margin-bottom: 20px;
}

.response-container p {
    margin-bottom: 10px;
}

.response-container a {
    display: block;
    text-align: center;
    margin-top: 20px;
    text-decoration: none;
    color: #007bff;
}
</style>
"""

def responsePage(firstname, lastname, email, count):
    return """
    <html>
    <head>
        <title>User Information</title>
        """ + response_page_css + """
    </head>
    <body>
        <div class="response-container">
            <h2>User Information</h2>
            <p><strong>First Name:</strong> """ + str(firstname) + """</p>
            <p><strong>Last Name:</strong> """ + str(lastname) + """</p>
            <p><strong>Email:</strong> """ + str(email) + """</p>
            <p><strong>Word Count:</strong> """ + str(count) + """</p>
            <a href="/download">Download</a>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
  app.run()
