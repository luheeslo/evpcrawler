import requests
from lxml import html
import json

url = 'https://www.euvoupassar.com.br'
login_url = 'https://www.euvoupassar.com.br/login/index/autenticar'
cursos_url = 'https://www.euvoupassar.com.br/cursos/indice'


def login(email, senha):
    session = requests.session()
    auth = {
        'email': email,
        'senha': senha
    }
    response = session.post(login_url, data=auth)
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
        page = self._session.get(cursos_url, allow_redirects=False)
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
                    url_aulas = curso.xpath('span/a/@href')[0]
                    yield nome_curso, url_aulas

    def aulas(self, url_aulas):
        page = self._session.get(url_aulas, allow_redirects=False)
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
                True if mp4 else False,
                True if pdf else False
            )
