"""
Aqui, definimos as enumerações.
"""

class Status:
    SUCESSO = "sucesso"
    FALHA = "falha"

class Retorno:
    """
    Serve para encapsular o dicionário de retorno da API.
    Informa o status (sucesso ou falha), o resultado (da realização da tarefa)
    e uma lista de mensagens destinadas ao usuário.
    """
    status = None
    resultado = None
    mensagens = None

    def __init__(self):
        self.status = ''
        self.resultado = ''
        self.mensagens = []

    def falhar(self, msg):
        """
        Adiciona uma mensagem de falha e já seta o status de falha.
        """
        self.status = Status.FALHA
        self.adicionar(msg)

    def suceder(self, msg):
        """
        Adiciona uma mensagem de sucesso e já seta o status de sucesso.
        """
        self.status = Status.SUCESSO
        self.adicionar(msg)

    def adicionar(self, msg):
        """
        Serve para dar um append numa mensagem. Ignora mensagens vazias.
        """
        if not isinstance(msg, (str, list)):
            raise Exception("Mensagem precisa ser do tipo string ou list")

        if msg:
            if isinstance(msg, str):
                self.mensagens.append(msg)
            elif isinstance(msg, list):
                self.mensagens.extend(msg)

    def get(self):
        """
        Organiza as informações num dicionário.
        """

        if self.status == '':
            self.status = Status.SUCESSO
        retorno = {
            "status": self.status,
            "resultado": self.resultado,
            "mensagens": self.mensagens
        }
        return retorno