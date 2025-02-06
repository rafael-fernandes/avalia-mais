from flask import Flask, render_template, request, redirect, url_for, flash
from database import Database
from routes import index, login, enquetes, nova_enquete

app = Flask(__name__)

app.secret_key = 'ppaH4u5LWhP2fVa3eM3ySLzfFiAdrMcs'

db = Database('database.db')

@app.before_request
def inicializa_banco():
  db.inicializa_o_banco()

app.add_url_rule('/', 'index', index)
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/enquetes', 'enquetes', enquetes, methods=['GET', 'POST'])
app.add_url_rule('/nova_enquete', 'nova_enquete', nova_enquete, methods=['GET'])

if __name__ == '__main__':
  app.run(debug=True)