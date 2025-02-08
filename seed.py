from database import Database  # Supondo que sua classe Database está em database.py

def seed_usuarios(db):
  # Lista de usuários para inserir
  usuarios = [
    ("Rafael", "rafael@email.com", "aluno", "senha123"),
    ("Hudson", "hudson@email.com", "aluno", "senha123"),
    ("Edna", "edna@email.com", "professor", "senha123"),
    ("UnB", "unb@email.com", "instituicao", "senha123")
  ]

  # Criar os usuários usando o método da classe Database
  for nome, email, perfil, senha in usuarios:
    db.criar_usuario(nome, email, perfil, senha)

  print("Seed de usuários concluída com sucesso!")
