from django.conf import settings
from json import loads
from os.path import isfile
from web3 import Web3


"""
Configurar conexão ao node
"""
provider = Web3.IPCProvider(settings.IPC_PATH)
w3 = Web3(provider)

def checar_conexao(completo=False):
    """
    Serve para verificar se está tudo OK para acessar o contrato na rede ethereum
    :return: True/False
    """

    """
    Verifica se existe um nó rodando
    """
    if not w3.isConnected():
        raise Exception("Conexão ao node falhou. Existe um console geth rodando no IPC_PATH %s?" % settings.IPC_PATH)

    if completo:

        """
        Verifica se existe o arquivo de configuração do contrato
        """
        if not isfile(settings.ABI_PATH):
            raise Exception("não foi encontrado um arquivo ABI que descreve o contrato no ABI_PATH %s" % settings.ABI_PATH)


        """
        Verifica se o endereço está setado corretamente
        """
        if not w3.isChecksumAddress(settings.ENDERECO_ETH):
            raise Exception("Endereço configurado incorretamente. Está convertido para checksum?")



checar_conexao(completo=True)
"""
Configurar conta
"""
w3.personal.unlockAccount(settings.ENDERECO_ETH, settings.PASSPHRASE_ETH)

"""
Configurar contrato
"""
arquivo_abi = open(settings.ABI_PATH)
abi = loads(arquivo_abi.read())
arquivo_abi.close()

contrato = w3.eth.contract(
    address=settings.ENDERECO_CONTRATO_ETH,
    abi=abi,
)

if not contrato.functions.consultarOficial(settings.ENDERECO_ETH).call():
    raise Exception("O endereço configurado não tem as permissões necessárias.")


# TODO: e se não tiver saldo suficiente para transacionar?

class Blockchain:
    """
    Essa classe gerencia o contato com o smart contract criado na rede Ethereum.
    Verifica saldo de usuários, e debita
    """

    def verificar_saldo(self, endereco):
        """
        :param endereco: endereço na blockchain
        :return: saldo de créditos disponível
        """

        checar_conexao()

        addr = w3.toChecksumAddress(endereco)

        return contrato.functions.consultarSaldo(addr).call()

    def debitar_creditos(self, endereco, quantia):
        """
        :param endereco: endereço na blockchain
        :param quantia: quantia de créditos a ser debitada do saldo
        :return: True se débito realizado com sucesso, se não, False
        """

        checar_conexao()

        addr = w3.toChecksumAddress(endereco)

        contrato.transact({"from":settings.ENDERECO_ETH}).debitar(addr, quantia)

    def validar_usuario(self, endereco):
        """
        Verifica se o endereço passado é válido.

        Se for um endereço válido, mas não estiver convertido para checksum, realiza a conversão.
        """

        try:
            return w3.toChecksumAddress(endereco)
        except ValueError:
            return ''
