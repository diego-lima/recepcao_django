from django.conf import settings
from json import loads
from os.path import isfile
from web3 import Web3


"""
Se pythonanywhere == True, então vamos pular todas as interações com o nó
ou com a blockchain
"""

pythonanywhere = True


"""
Configurar conexão ao node
"""
provider = Web3.IPCProvider(settings.IPC_PATH)
w3 = Web3(provider)


def checar_conexao(completo=False):
    """
    Serve para verificar se está tudo OK para acessar o contrato na rede ethereum:
    - Se existe um nó rodando na rede
    - Se o ABI pode ser encontrado
    - Se o endereço(sem ser o do contrato) foi setado corretamente.

    Se completo = False, só checamos se existe um nó na rede
    """

    if pythonanywhere:
        return

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
            raise Exception("não foi encontrado um arquivo ABI que descreve o contrato no ABI_PATH %s" %
                            settings.ABI_PATH)

        """
        Verifica se o endereço está setado corretamente
        """
        if not w3.isChecksumAddress(settings.ENDERECO_ETH):
            raise Exception("Endereço configurado incorretamente. Está convertido para checksum?")


if not pythonanywhere:
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
        raise Exception("O endereço configurado não tem as permissões necessárias para operar.")


# TODO: e se não tiver saldo suficiente para transacionar?

class Blockchain:
    """
    Essa classe gerencia o contato com o smart contract criado na rede Ethereum.
    Verifica saldo de usuários, e debita
    """

    @staticmethod
    def verificar_saldo(endereco):
        """
        :param endereco: endereço na blockchain
        :return: saldo de créditos disponível
        """
        if pythonanywhere:
            return 100

        checar_conexao()

        addr = w3.toChecksumAddress(endereco)

        return contrato.functions.consultarSaldo(addr).call()

    @staticmethod
    def pagar(endereco, quantia, passphrase, unidade="ether"):
        """
        Realiza uma transação para o contrato a partir das informações fornecidas
        pelo usuário.

        :param endereco: do usuário
        :param quantia: a ser transferida
        :param passphrase: da conta do usuário
        :param unidade: da quantia (se é em ether ou em wei)
        :return:
        """

        if pythonanywhere:
            return "Executando sem acesso à blockchain."

        checar_conexao()

        if unidade.lower() == "ether":
            valor = w3.toWei(quantia, "ether")
        elif unidade.lower() != "wei":
            raise Exception("Unidade de pagamento inválida. Tente wei ou ether")
        else:
            valor = quantia

        transacao = {
            "from": endereco,
            "to": settings.ENDERECO_CONTRATO_ETH,
            "value": valor
        }

        if w3.personal.unlockAccount(endereco, passphrase):
            retorno = w3.eth.sendTransaction(transacao)
            w3.personal.lockAccount(endereco)
        else:
            retorno = "Não foi possível desbloquear a conta. Os dados de acesso (endereço e passphrase) conferem?"

        return retorno

    @staticmethod
    def debitar_creditos(endereco, quantia):
        """
        :param endereco: endereço na blockchain
        :param quantia: quantia de créditos a ser debitada do saldo
        :return: True se débito realizado com sucesso, se não, False
        """

        if pythonanywhere:
            return

        checar_conexao()

        addr = w3.toChecksumAddress(endereco)

        contrato.transact({"from": settings.ENDERECO_ETH}).debitar(addr, quantia)

    @staticmethod
    def validar_usuario(endereco):
        """
        Verifica se o endereço passado é válido.

        Se for um endereço válido, mas não estiver convertido para checksum, realiza a conversão.
        """

        try:
            return w3.toChecksumAddress(endereco)
        except ValueError:
            return ''
