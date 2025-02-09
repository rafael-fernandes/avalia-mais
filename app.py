from flask import Flask, render_template, request, redirect, url_for, flash
from routes import index, login, cadastro, logout, professor_enquetes, professor_nova_enquete, aluno_enquetes, aluno_ver_respostas, responder_enquete, professor_ver_resultados, instituicao_enquetes, instituicao_ver_resultados
from database import Database
from auth import Auth

app = Flask(__name__)

app.secret_key = 'ppaH4u5LWhP2fVa3eM3ySLzfFiAdrMcs'

auth = Auth(app)

db = Database('database.db')

# Inicializa o banco de dados
db.inicializa_o_banco()

# Define as rotas
app.add_url_rule('/', 'index', index)
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/cadastro', 'cadastro', cadastro, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout)
app.add_url_rule('/professor/enquetes', 'professor_enquetes', professor_enquetes, methods=['GET', 'POST'])
app.add_url_rule('/professor/nova_enquete', 'professor_nova_enquete', professor_nova_enquete)
app.add_url_rule('/aluno/enquetes', 'aluno_enquetes', aluno_enquetes)
app.add_url_rule('/aluno/ver_respostas/<int:enquete_id>', 'aluno_ver_respostas', aluno_ver_respostas)
app.add_url_rule('/responder_enquete/<int:enquete_id>', 'responder_enquete', responder_enquete, methods=['GET', 'POST'])
app.add_url_rule('/professor/ver_resultados/<int:enquete_id>', 'professor_ver_resultados', professor_ver_resultados)
app.add_url_rule('/instituicao/enquetes', 'instituicao_enquetes', instituicao_enquetes)
app.add_url_rule('/instituicao/ver_resultados/<int:enquete_id>', 'instituicao_ver_resultados', instituicao_ver_resultados)

if __name__ == '__main__':
  app.run(debug=True, port=3000)