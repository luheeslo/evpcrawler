"""
File: util.py
Author: lhel
Email: luheeslo@gmail.com
Github: https://github.com/luheeslo
Description: Module with helper funcions
"""
import os


def download(nome_arquivo, path, response):
    """Baixa arquivos via  HTTP e salva no disco rígido

    :nome_arquivo: nome do arquivo a ser gravado
    :path: caminho do diretório onde o arquivo será salvo
    :response: objeto de resposta de uma requisição HTTP
    :returns: generator que produz uma tupla com os bytes baixados
    e o tamaho total do arquivo

    """
    path = os.path.join(path, nome_arquivo)
    tamanho_arquivo = int(response.headers['content-length'])
    bytes_enviados = 0
    with open(path, 'wb') as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)
            bytes_enviados += len(chunk)
            yield bytes_enviados, tamanho_arquivo

