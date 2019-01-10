from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from os import path
from json import dumps

from .tipos import Status, Retorno
from .blockchain import Blockchain

import python3_gearman as gearman

# Create your views here.

class FileView(APIView):
    """Teste de upload de arquivo e armazenamento no diretório de mediaj"""
    # Usamos os dois parsers abaixo para suportar completamente o envio de forms, incluido upload de arquivos
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):

        filefieldname = "hiho"
        if filefieldname not in request.FILES:
            return Response("cade o arquivo? a chave deve ser %s" % filefieldname, status=status.HTTP_400_BAD_REQUEST)

        filepath = path.join(settings.MEDIA_ROOT, request.FILES[filefieldname].name)

        with open(filepath, "wb+") as myf:
            # Iterar nos chunks do arquivo para não sobrecarregar memória
            for chunk in request.FILES[filefieldname].chunks():
                myf.write(chunk)

        return Response("fala tuuuUuUuU", status=status.HTTP_201_CREATED)


class ProcessView(APIView):
    """Teste de uso do Gearman para repassar carga de trabalho para o core"""

    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        gm_client = gearman.GearmanClient(['localhost:4730'])

        try:
            completed_job_request = gm_client.submit_job("process", dumps(request.data))
        except Exception as e:
            msg = u"Deu erro na requsição: %s" % e.args[0]
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        else:
            msg = check_request_status(completed_job_request)

        return Response(msg, status=status.HTTP_200_OK)

class MNISTPredictView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    # O preço de utilização do serviço em créditos
    preco = 1
    # O nome da atividade que é realizada no lado do core
    atividade = "MNISTProcess"

    def post(self, request, *args, **kwargs):
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

        nome_chave_endereco = "endereco"
        if nome_chave_endereco not in request.data:
            retorno.status = Status.FALHA
            retorno.adicionar("Informe o endereço do usuário sob a chave '%s'" % nome_chave_endereco)
            return Response(retorno.get(), status=status.HTTP_400_BAD_REQUEST)

        blkn = Blockchain()
        usuario = blkn.validar_usuario(request.data[nome_chave_endereco])

        if not usuario:
            retorno.status = Status.FALHA
            retorno.adicionar("Endereço informado não é válido")
            return Response(retorno.get(), status=status.HTTP_400_BAD_REQUEST)

        if blkn.verificar_saldo(usuario) < self.preco:
            retorno.status = Status.FALHA
            retorno.adicionar("Saldo insuficiente.")
            return Response(retorno.get(), status=status.HTTP_402_PAYMENT_REQUIRED)

        blkn.debitar_creditos(usuario, self.preco)
        retorno.adicionar("Pagamento realizado")

        """
        Salvar a imagem em disco
        """
        nome_chave_imagem = "data"
        if nome_chave_imagem not in request.FILES:
            retorno.status = Status.FALHA
            retorno.adicionar("Faça upload do arquivo de imagem sob a chave '%s'" % nome_chave_imagem)
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
        # TODO: retornar falha caso não haja um worker disponível

        try:
            requisicao_execucao = gm_client.submit_job(self.atividade, caminho_imagem)
        except Exception as e:
            retorno.status = Status.FALHA
            retorno.adicionar("Deu erro na requsição: %s" % e.args[0])
            # TODO: estornar pagamento
        else:
            analise_execucao = check_request_status(requisicao_execucao)
            # Se tiver warnings, entendemos que houve falha na execução
            if not analise_execucao['warnings']:
                retorno.status = Status.SUCESSO
                retorno.adicionar("Tarefa completada.")
            else:
                retorno.status = Status.FALHA
                retorno.adicionar(analise_execucao["warnings"])
                # TODO: estornar pagamento

            retorno.resultado = analise_execucao["resultado"]

        return Response(retorno.get(), status=status.HTTP_200_OK)


def check_request_status(job_request):
    """
    Serve para analisar o resultado da execução através do Gearman.
    Retorna o resultado da execução, o estado e os warnings lançados.
    """
    status = ''
    resultado = ''
    warnings = []
    if job_request.complete:
        status = job_request.state
        warnings.extend(job_request.warning_updates)
        resultado = job_request.result
    elif job_request.timed_out:
        warnings.append("Time out")

    retorno = {
        "status": status,
        "resultado": resultado,
        "warnings": warnings
    }
    return retorno
