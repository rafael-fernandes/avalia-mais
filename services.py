from collections import defaultdict

class PerguntasService:
  @staticmethod
  def get_perguntas():
    return {
      '1': 'O professor explicou o conteúdo de forma clara e compreensível?',
      '2': 'O ritmo da aula foi adequado?',
      '3': 'O material utilizado (slides, quadros, etc.) foi útil?',
      '4': 'O professor demonstrou domínio do assunto?',
      '5': 'A carga de trabalho da disciplina é adequada?',
      '6': 'O conteúdo da aula foi relevante para o curso?',
      '7': 'O professor utilizou exemplos práticos para ilustrar o conteúdo?',
      '8': 'O ambiente de aula (físico ou virtual) foi adequado?',
      '9': 'Você recomendaria este professor para outros alunos?',
      '10': 'O professor foi receptivo a dúvidas e questionamentos?'
    }

class EnqueteService:
  def __init__(self, respostas):
    """ Inicializa o serviço com uma lista de respostas no formato (numero_pergunta, resposta). """
    self.respostas_dict = defaultdict(list)

    for numero, resposta in respostas:
      self.respostas_dict[numero].append(resposta)

  def media_respostas(self, numero_pergunta):
    """ Calcula a média das respostas para uma pergunta específica. """
    if numero_pergunta in self.respostas_dict:
      lista_respostas = self.respostas_dict[numero_pergunta]
      return sum(lista_respostas) / len(lista_respostas)
      
    return None  # Retorna None se a pergunta não existir
