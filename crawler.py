import os
import requests
from lxml import html
import json

URL = 'https://www.euvoupassar.com.br'
LOGIN_URL = 'https://www.euvoupassar.com.br/login/index/autenticar'
CURSOS_URL = 'https://www.euvoupassar.com.br/cursos/indice'
DOWNLOAD_URL = 'https://www.euvoupassar.com.br/application/download/'


def login(email, senha):
    session = requests.session()
    auth = {
        'email': email,
        'senha': senha
    }
    response = session.post(LOGIN_URL, data=auth)
    json_response = json.loads(response.content.decode('utf-8'))
    mensagem = json_response['mensagem']
    if mensagem == 'Acesso liberado. Aguarde...':
        print(mensagem)
        return EvpCrawler(session)
    else:
        print(mensagem)


class EvpCrawler:

    def __init__(self, session):
        self._session = session

    def materias(self):
        page = self._session.get(CURSOS_URL, allow_redirects=False)
        tree = html.fromstring(page.content)

        lis_query = '/html/body/div[1]/section/div/div[2]/div/section/ul/li'

        materias = tree.xpath(lis_query)
        for li_materia in materias:
            nome_materia = li_materia.xpath('span/text()')[0]
            yield nome_materia, li_materia

    def cursos(self, nome_materia):
        for materia in self.materias():
            if materia[0] == nome_materia:
                cursos = materia[1].xpath('ul/li')
                for curso in cursos:
                    nome_curso = curso.xpath('span/text()')[0]
                    aulas_url = curso.xpath('span/a/@href')[0]
                    yield nome_curso, aulas_url

    def aulas(self, aulas_url):
        page = self._session.get(aulas_url, allow_redirects=False)
        tree = html.fromstring(page.content)

        aulas = tree.xpath('//div[@class="bloco-branco"]/ul/li')
        for aula in aulas:
            titulo_aula = aula.xpath('span/a/text()')[0]
            data_aula = aula.xpath('div/div/@data-aula')[0]
            mp4 = aula.xpath('div/div/a[@class="mp4 baixarMP4 "]')
            pdf = aula.xpath('div/div/a[@class="pdf baixarPDF "]')
            yield (
                titulo_aula,
                data_aula,
                'mp4' if mp4 else '',
                'pdf' if pdf else ''
            )

    def baixarAula(self, data_aula, mp4, pdf, path=''):
        for type in (mp4, pdf):
            if type:
                response = self._session.post(DOWNLOAD_URL + type,
                                              data={'id': data_aula})
                json_response = json.loads(response.content.decode('utf-8'))
                url = json_response['url']
                response = self._session.get(json_response['url'], stream=True)
                if response.status_code == 200:
                    nome_arquivo = url.split('/').pop()
                    path = os.path.join(path, nome_arquivo)
                    tamanho_arquivo = int(response.headers['content-length'])
                    bytes_enviados = 0
                    with open(path, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                            bytes_enviados += len(chunk)
                            yield bytes_enviados, tamanho_arquivo
