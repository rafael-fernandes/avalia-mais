import sqlite3
from flask import flash
from datetime import datetime
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
  def __init__(self, db_name):
    self.db_name = db_name

  def _connect(self):
    """Conecta ao banco de dados e retorna a conexão"""
    return sqlite3.connect(self.db_name)

  def inicializa_o_banco(self):
    """Inicializa o banco de dados com as tabelas necessárias"""
    try:
      conn = self._connect()
      cursor = conn.cursor()

      cursor.execute('''
        CREATE TABLE IF NOT EXISTS enquetes (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          titulo TEXT NOT NULL,
          perguntas TEXT,
          usuario_id INTEGER NOT NULL,
          criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );
      ''')

      cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          nome TEXT NOT NULL,
          email TEXT NOT NULL UNIQUE,
          senha TEXT NOT NULL,
          perfil TEXT DEFAULT 'aluno',
          criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
      ''')

      cursor.execute('''
        CREATE TABLE IF NOT EXISTS respostas (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          usuario_id INTEGER NOT NULL,
          enquete_id INTEGER NOT NULL,
          numero_pergunta INTEGER NOT NULL,
          resposta INTEGER NOT NULL CHECK(resposta >= 0 AND resposta <= 10),
          criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
          FOREIGN KEY (enquete_id) REFERENCES enquetes(id) ON DELETE CASCADE
        );
      ''')

      conn.close()
    except Exception as e:
      flash('Erro ao inicializar o banco de dados: ' + str(e))

  def criar_usuario(self, nome, email, perfil, senha):
    """Cria um novo usuário no banco de dados"""
    try:
      conn = self._connect()
      cursor = conn.cursor()

      cursor.execute('INSERT INTO usuarios (nome, email, perfil, senha) VALUES (?, ?, ?, ?)', (nome, email, perfil, generate_password_hash(senha)))

      conn.commit()
      conn.close()

      return True
    except Exception as e:
      return False
    
  def recuperar_usuario(self, id):
    """Recupera um usuário pelo ID"""
    conn = self._connect()
    cursor = conn.cursor()

    cursor.execute('SELECT id, email, nome, senha, perfil FROM usuarios WHERE id = ?', (id,))
    usuario = cursor.fetchone()

    conn.close()

    if usuario:
      return User(usuario[0], usuario[1], usuario[2], usuario[3], usuario[4])
    else:
      return None

  def recuperar_professores(self):
    """Recupera todos os professores do banco de dados"""
    conn = self._connect()
    cursor = conn.cursor()

    cursor.execute('SELECT id, email, nome FROM usuarios WHERE perfil = "professor"')
    professores = cursor.fetchall()

    conn.close()

    return professores

  def autenticar_usuario(self, email, senha):
    """Autentica um usuário no banco de dados"""
    try:
      conn = self._connect()
      cursor = conn.cursor()

      cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
      usuario = cursor.fetchone()

      conn.close()

      if usuario and check_password_hash(usuario[3], senha):
        return usuario
      else:
        return None
    except Exception as e:
      flash('Erro ao autenticar usuário: ' + str(e))
      return None

  def recuperar_enquetes(self, usuario_id=None):
    """Retorna todas as enquetes do banco de dados"""
    try:
      conn = self._connect()
      cursor = conn.cursor()

      if usuario_id:
        cursor.execute('SELECT * FROM enquetes WHERE usuario_id = ?', (usuario_id,))
      else:
        cursor.execute('SELECT * FROM enquetes')

      enquetes = cursor.fetchall()

      # mapeie enquetes para um objeto com os ids, títulos e perguntas
      enquetes = [{'id': enquete[0],
                  'titulo': enquete[1],
                  'perguntas': enquete[2],
                  'usuario_id': enquete[3],
                  'criado_em': datetime.strptime(enquete[4], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')}
                  for enquete in enquetes]

      conn.close()

      return enquetes
    except Exception as e:
      flash('Erro ao buscar enquetes: ' + str(e))
      return []

  def recuperar_enquetes_disponiveis(self, usuario_id):
    # selecione as enquetes que não possuem respostas para o usuario_id
    try:
      conn = self._connect()
      cursor = conn.cursor()

      cursor.execute('''
        SELECT e.id, e.titulo, e.criado_em
        FROM enquetes e
        WHERE e.id NOT IN (
          SELECT DISTINCT enquete_id
          FROM respostas
          WHERE usuario_id = ?
        )
      ''', (usuario_id,))

      enquetes = cursor.fetchall()

      # mapeie enquetes para um objeto com os ids, títulos e perguntas
      enquetes = [{'id': enquete[0],
                  'titulo': enquete[1],
                  'criado_em': datetime.strptime(enquete[2], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')}
                  for enquete in enquetes]

      conn.close()

      return enquetes
    except Exception as e:
      flash('Erro ao buscar enquetes: ' + str(e))
      return []

  def recuperar_enquetes_respondidas(self, usuario_id):
    # selecione as enquetes que possuem respostas para o usuario_id
    try:
      conn = self._connect()
      cursor = conn.cursor()

      cursor.execute('''
        SELECT e.id, e.titulo, e.criado_em
        FROM enquetes e
        WHERE e.id IN (
          SELECT DISTINCT enquete_id
          FROM respostas
          WHERE usuario_id = ?
        )
      ''', (usuario_id,))

      enquetes = cursor.fetchall()

      # mapeie enquetes para um objeto com os ids, títulos e perguntas
      enquetes = [{'id': enquete[0],
                  'titulo': enquete[1],
                  'criado_em': datetime.strptime(enquete[2], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')}
                  for enquete in enquetes]

      conn.close()

      return enquetes
    except Exception as e:
      flash('Erro ao buscar enquetes: ' + str(e))

  def recuperar_enquete(self, enquete_id):
    """Recupera uma enquete pelo ID"""
    conn = self._connect()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM enquetes WHERE id = ?', (enquete_id,))
    enquete = cursor.fetchone()

    conn.close()

    if enquete:
      return {
        'id': enquete[0],
        'titulo': enquete[1],
        'perguntas': enquete[2].split(','),
        'usuario_id': enquete[3],
        'criado_em': datetime.strptime(enquete[4], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
      }
    else:
      return None

  def criar_enquete(self, titulo, perguntas, usuario_id):
    """Cria uma nova enquete no banco de dados"""
    try:
      conn = self._connect()
      cursor = conn.cursor()

      cursor.execute('INSERT INTO enquetes (titulo, perguntas, usuario_id, criado_em) VALUES (?, ?, ?, ?)', (titulo, ','.join(perguntas), usuario_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

      conn.commit()
      conn.close()

      return True
    except Exception as e:
      return False

  def salvar_resposta(self, usuario_id, enquete_id, numero_pergunta, resposta):
    """Salva uma resposta no banco de dados"""
    try:
      conn = self._connect()
      cursor = conn.cursor()

      cursor.execute('INSERT INTO respostas (usuario_id, enquete_id, numero_pergunta, resposta) VALUES (?, ?, ?, ?)', (usuario_id, enquete_id, numero_pergunta, resposta))

      conn.commit()
      conn.close()

      return True
    except Exception as e:
      return False
  
  def recuperar_respostas(self, enquete_id, usuario_id=None):
    """Recupera as respostas de uma enquete"""
    conn = self._connect()
    cursor = conn.cursor()

    if usuario_id:
      cursor.execute('SELECT numero_pergunta, resposta FROM respostas WHERE enquete_id = ? AND usuario_id = ?', (enquete_id, usuario_id))
    else:
      cursor.execute('SELECT numero_pergunta, resposta FROM respostas WHERE enquete_id = ?', (enquete_id,))

    respostas = cursor.fetchall()

    conn.close()

    return respostas
