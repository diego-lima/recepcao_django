from rest_framework import status
from rest_framework.response import Response

from .blockchain import Blockchain
from .tipos import Retorno


def validar_quantia(quantia):
    """
    Valida uma quantia passada pelo usuário.
    Retorna 0 se a validação falhar.
    """
    try:
        float(quantia)
        return float(quantia)
    except ValueError:
        return 0


def validar_unidade(unidade):
    """
    Valida se a unidade passada é aceita: Wei ou ether.
    Retorna '' se a validação falhar.
    """

    if unidade.lower() not in ['ether', 'wei']:
        return ''

    return unidade.lower()

def validar_passphase(passphrase):
    """
    Valida se o passphrase é válido.
    Retorna '' se a validação falhar.
    """
    # TODO
    if not passphrase:
        return ''
    return passphrase


def verificar_endereco_usuario(chave, metodo='get'):
    """
    Decorator que pega o objeto request da view e verifica se um endereço
    de usuário foi informado corretamente
    :param chave: o campo onde buscar o endereço
    :param metodo: se o request é de um get ou post
    """
    def meu_decorator(func):

        def func_wrapper(request, *args, **kwargs):
            retorno = Retorno()

            """
            Se for get ou post, vamos procurar em um lugar diferente
            getter será o método "get" da requisição, ou dentro de GET ou de POST
            """
            if metodo.lower() == 'get':
                getter = request.GET.get
            elif metodo.lower() == 'post':
                getter = request.POST.get
            else:
                raise Exception('método inválido no decorator de verificar usuario')

            """
            Vemos se não está faltando o campo ou se seu valor é inválido
            """
            if not getter(chave, None):
                retorno.falhar("Informe o endereço do usuário sob a chave '%s'" % chave)
                return Response(retorno.get(), status=status.HTTP_400_BAD_REQUEST)

            blkn = Blockchain()
            usuario = blkn.validar_usuario(getter(chave))

            if not usuario:
                retorno.falhar("Endereço informado não é válido")
                return Response(retorno.get(), status=status.HTTP_400_BAD_REQUEST)

            """
            Dando continuidade à execução
            """
            return func(request, *args, **kwargs)

        return func_wrapper
    return meu_decorator
