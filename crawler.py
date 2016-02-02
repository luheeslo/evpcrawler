import requests
from lxml import html
import json
from util import download


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
            types = (
                'mp4' if mp4 else '',
                'pdf' if pdf else ''
            )
            yield {
                'titulo_aula': titulo_aula,
                'data_aula': data_aula,
                'types': types
            }

    def baixarAula(self, data_aula, type, path=''):
        response = self._session.post(DOWNLOAD_URL + type,
                                      data={'id': data_aula})

        json_response = json.loads(response.content.decode('utf-8'))
        url = json_response['url']
        response = self._session.get(json_response['url'], stream=True)
        if response.status_code == 200:
            nome_arquivo = url.split('/').pop()
            return download(nome_arquivo, path, response)

