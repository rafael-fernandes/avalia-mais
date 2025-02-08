from flask import Flask, render_template, request, redirect, url_for, flash
from routes import index, login, logout, professor_enquetes, professor_nova_enquete, aluno_enquetes, responder_enquete
from database import Database
from auth import Auth
from seed import seed_usuarios

app = Flask(__name__)

app.secret_key = 'ppaH4u5LWhP2fVa3eM3ySLzfFiAdrMcs'

auth = Auth(app)

db = Database('database.db')

@app.before_request
def inicializa_banco():
  db.inicializa_o_banco()

# Executar o seed
seed_usuarios(db)

app.add_url_rule('/', 'index', index)
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout)
app.add_url_rule('/professor/enquetes', 'professor_enquetes', professor_enquetes, methods=['GET', 'POST'])
app.add_url_rule('/professor/nova_enquete', 'professor_nova_enquete', professor_nova_enquete)
app.add_url_rule('/aluno/enquetes', 'aluno_enquetes', aluno_enquetes)
app.add_url_rule('/responder_enquete/<int:enquete_id>', 'responder_enquete', responder_enquete, methods=['GET', 'POST'])

if __name__ == '__main__':
  app.run(debug=True, port=3000)