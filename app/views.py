from django.conf import settings
from hexbytes.main import HexBytes
from os import path
import python3_gearman as gearman
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from web3 import Web3

from .utils import verificar_endereco_usuario, validar_quantia, validar_unidade, validar_passphase
from .tipos import Retorno
from .blockchain import Blockchain as Blkn



@api_view(['GET'])
@verificar_endereco_usuario('endereco')
def saldo_consultar(request):
    """
    Realiza consulta de saldo na blockchain. O retorno é a quantia de créditos
    ainda disponível"""

    retorno = Retorno()

    chave_endereco = 'endereco'

    usuario = Blkn.validar_usuario(request.GET[chave_endereco])

    retorno.resultado = Blkn.verificar_saldo(usuario)

    return Response(retorno.get(), status=status.HTTP_200_OK)


@api_view(['POST'])
@verificar_endereco_usuario('endereco', 'POST')
def saldo_pagar(request):
    """
    Realiza compra de créditos.
    O usuário deve informar o seu endereço, a quantia que deseja pagar
    e a unidade da quantia (se é em ether ou em wei). Padrão assumido ether.
    Também deve informar sua passphrase para que eu possa realizar o pagamento
    em nome dele"""

    retorno = Retorno()

    # Chaves que vamos buscar os valores no request
    chave_endereco = 'endereco'
    chave_quantia = 'quantia'
    chave_unidade = 'unidade'
    chave_passphrase = 'passphrase'

    """
    Validar a quantia
    """
    if chave_quantia not in request.data:
        retorno.falhar("Informe a quantia para ser transferida ao contrato sob a chave %s." % chave_quantia)
        return Response(retorno.get(), status=status.HTTP_400_BAD_REQUEST)

    quantia = validar_quantia(request.data[chave_quantia])

    """
    Validar a unidade
    """
    if chave_unidade not in request.data:
        """
        Estamos assumindo que ninguém transferiria um valor tão grande quanto 1000
        se fosse ether."""
        if quantia > 1000:
            retorno.adicionar("Assumindo pagamento feito em Wei")
            unidade = "wei"
        else:
            retorno.adicionar("Assumindo pagamento feito em ether")
            unidade = "ether"
    else:
        unidade = validar_unidade(request.data[chave_unidade])

    if not unidade:
        retorno.falhar("Unidade de pagamento inválida. Tente wei ou ether")
        return Response(retorno.get(), status=status.HTTP_400_BAD_REQUEST)

    """
    Validar o passphrase
    """
    if chave_passphrase not in request.data:
        retorno.falhar("Informe a passphrase para poder fechar a transação sob a chave %s." % chave_passphrase)
        return Response(retorno.get(), status=status.HTTP_400_BAD_REQUEST)

    passphrase = validar_passphase(request.data[chave_passphrase])

    if not passphrase and passphrase != '':
        retorno.falhar("Passphrase inválida.")
        return Response(retorno.get(), status=status.HTTP_400_BAD_REQUEST)

    """
    Validar o usuário e tentar realizar a transação com as credenciais informadas
    """

    usuario = Blkn.validar_usuario(request.data[chave_endereco])

    resultado = Blkn.pagar(usuario, quantia, passphrase, unidade)
    if isinstance(resultado, HexBytes):
        retorno.resultado = resultado.hex()
        retorno.adicionar("O resultado é o hash da transação.")
    else:
        # Se o resultado não for um HexBytes (o hash da transação), então será uma string mensagem
        retorno.falhar(resultado)
        return Response(retorno.get(), status=status.HTTP_400_BAD_REQUEST)

    return Response(retorno.get(), status=status.HTTP_200_OK)


class MNISTPredictView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    # O preço de utilização do serviço em créditos
    preco = 1
    # O nome da atividade que é realizada no lado do core
    atividade = "MNISTProcess"

    def get(self, request):
        """
        Retorna apenas o preço desse serviço, em ETH.
        Retorna também o valor em Wei.
        """

        retorno = Retorno()

        retorno.resultado = self.preco

        retorno.adicionar("O resultado foi o preço em Ether.")

        retorno.adicionar("Em Wei: %d" % Web3.toWei(self.preco, "ether"))

        return Response(retorno.get(), status=status.HTTP_200_OK)

    @verificar_endereco_usuario('endereco')
    def post(self, request):
        """
        Verifica se o usuário pagou.
        Recebe uma imagem de um dígito numérico.
        Salva essa imagem no disco.
        Lança um pedido pelo gearman para um worker rodando em outro processo resgatar essa imagem no disco
        e rodar uma CNN feita com Keras em cima dela."""

        retorno = Retorno()

        """
        Verificar se o usurário pagou para usar
        """

        chave_endereco = "endereco"

        usuario = Blkn.validar_usuario(request.data[chave_endereco])

        if Blkn.verificar_saldo(usuario) < self.preco:
            retorno.falhar("Saldo insuficiente.")
            return Response(retorno.get(), status=status.HTTP_402_PAYMENT_REQUIRED)

        Blkn.debitar_creditos(usuario, self.preco)
        retorno.adicionar("Pagamento realizado")

        """
        Salvar a imagem em disco
        """
        nome_chave_imagem = "data"
        if nome_chave_imagem not in request.FILES:
            retorno.falhar("Faça upload do arquivo de imagem sob a chave '%s'" % nome_chave_imagem)
            return Response(retorno.get(), status=status.HTTP_400_BAD_REQUEST)

        imagem = request.FILES[nome_chave_imagem]
        caminho_imagem = path.join(settings.MEDIA_ROOT, imagem.name)

        with open(caminho_imagem, "wb+") as myf:
            # Iterar nos chunks do arquivo para não sobrecarregar memória
            for chunk in imagem.chunks():
                myf.write(chunk)

        """
        Acionar o worker, passando o caminho para a imagem salva em disco
        """
        gm_client = gearman.GearmanClient(['localhost:4730'])
        # TODO: retornar falha caso não haja um worker disponível e estornar pagamento

        try:
            requisicao_execucao = gm_client.submit_job(self.atividade, caminho_imagem)
        except Exception as e:
            retorno.falhar("Deu erro na requsição: %s" % e.args[0])
            # TODO: estornar pagamento
        else:
            analise_execucao = check_request_status(requisicao_execucao)
            # Se tiver warnings, entendemos que houve falha na execução
            if not analise_execucao['warnings']:
                retorno.suceder("Tarefa completada.")
            else:
                retorno.falhar(analise_execucao["warnings"])
                # TODO: estornar pagamento

            retorno.resultado = analise_execucao["resultado"]

        return Response(retorno.get(), status=status.HTTP_200_OK)


def check_request_status(job_request):
    """
    Serve para analisar o resultado da execução através do Gearman.
    Retorna o resultado da execução, o estado e os warnings lançados.
    """
    estado = ''
    resultado = ''
    warnings = []
    if job_request.complete:
        estado = job_request.state
        warnings.extend(job_request.warning_updates)
        resultado = job_request.result
    elif job_request.timed_out:
        warnings.append("Time out")

    retorno = {
        "status": estado,
        "resultado": resultado,
        "warnings": warnings
    }
    return retorno
