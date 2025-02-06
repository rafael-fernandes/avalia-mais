import sqlite3
from flask import flash
from datetime import datetime

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
          criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
      ''')

      cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          nome TEXT NOT NULL,
          email TEXT NOT NULL UNIQUE,
          senha TEXT NOT NULL,
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

  def autenticar_usuario(self, email, senha):
    """Autentica um usuário no banco de dados"""
    try:
      conn = self._connect()
      cursor = conn.cursor()

      cursor.execute('SELECT * FROM usuarios WHERE email = ? AND senha = ?', (email, senha))
      usuario = cursor.fetchone()

      conn.close()

      return usuario
    except Exception as e:
      flash('Erro ao autenticar usuário: ' + str(e))
      return None

  def recuperar_enquetes(self):
    """Retorna todas as enquetes do banco de dados"""
    try:
      conn = self._connect()
      cursor = conn.cursor()

      cursor.execute('SELECT * FROM enquetes')
      enquetes = cursor.fetchall()

      # mapeie enquetes para um objeto com os ids, títulos e perguntas
      enquetes = [{'id': enquete[0],
                  'titulo': enquete[1],
                  'perguntas': enquete[2],
                  'criado_em': datetime.strptime(enquete[3], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')}
                  for enquete in enquetes]

      conn.close()

      return enquetes
    except Exception as e:
      flash('Erro ao buscar enquetes: ' + str(e))
      return []

  def criar_enquete(self, titulo, perguntas):
    """Cria uma nova enquete no banco de dados"""
    try:
      conn = self._connect()
      cursor = conn.cursor()

      cursor.execute('INSERT INTO enquetes (titulo, perguntas, criado_em) VALUES (?, ?, ?)', (titulo, ','.join(perguntas), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

      conn.commit()
      conn.close()

      flash('Enquete criada com sucesso!', 'success')
      return True
    except Exception as e:
      flash('Erro ao criar enquete: ' + str(e), 'danger')
      return False