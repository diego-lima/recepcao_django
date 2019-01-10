"""
Aqui, definimos as enumerações.
"""

class Status:
    SUCESSO = "sucesso"
    FALHA = "falha"

class Retorno:
    """
    Serve para encapsular o dicionário de retorno da API.
    """
    status = None
    resultado = None
    mensagens = None

    def __init__(self):
        self.status = ''
        self.resultado = ''
        self.mensagens = []

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
            raise Exception("Retorno sem status configurado")
        retorno = {
            "status": self.status,
            "resultado": self.resultado,
            "mensagens": self.mensagens
        }
        return retorno