import os
import requests
from lxml import html
import json

url = 'https://www.euvoupassar.com.br'
login_url = 'https://www.euvoupassar.com.br/login/index/autenticar'
cursos_url = 'https://www.euvoupassar.com.br/cursos/indice'
auth = {
    'email': os.environ.get('EVP_EMAIL'),
    'senha': os.environ.get('EVP_PASSWORD')
}


def main():
    session = requests.session()
    response = session.post(login_url, data=auth)
    json_response = json.loads(response.content.decode('utf-8'))
    mensagem = json_response['mensagem']
    if mensagem == 'Acesso liberado. Aguarde...':
        print(mensagem)
        page = session.get(cursos_url)
        page = session.get(cursos_url)
        tree = html.fromstring(page.content)
        lis_query = '/html/body/div[1]/section/div/div[2]/div/section/ul/li'
        materias = tree.xpath(lis_query)
        for materia in materias:
            print(materia.xpath('span/text()'))
    else:
        print(mensagem)

if __name__ == '__main__':
    main()
