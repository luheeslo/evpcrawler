"""
File: util.py
Author: lhel
Email: luheeslo@gmail.com
Github: https://github.com/luheeslo
Description: Module with helper funcions
"""
import os
import requests


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


class Session():
        __logged = False
        __email = ''
        __senha = ''
        __session = None

        @classmethod
        def login(cls, email, senha, login_url):
            if cls.__email == email and cls.__senha == senha:
                if email == '' and senha == '':
                    raise Exception('Necessário email e login')
                return cls.__session, cls.__logged
            else:
                cls.__email = email
                cls.__senha = senha
                auth = {
                    'email': email,
                    'senha': senha
                }

            cls.__session = requests.session()
            response = cls.__session.post(login_url, data=auth)
            json_response = response.json()
            mensagem = json_response['mensagem']
            if json_response['mensagem'] == 'Acesso liberado. Aguarde...':
                cls.__logged = True
            return cls.__session, mensagem



