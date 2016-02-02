#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from crawler import login


"""
File: cli.py
Author: lhel
Email: luheeslo@gmail.com
Github: https://github.com/luheeslo
Description: Interface de linha de comando para acesso ao conteúdo do
Eu Vou Passar
"""

import argparse

EMAIL = os.getenv('EVP_EMAIL')
SENHA = os.getenv('EVP_PASSWORD')
PATH = os.getenv('DOWNLOAD_PATH')

SESSION = login(EMAIL, SENHA)


def mostrar_materias(count=-1):
    crawler = SESSION
    materias = crawler.materias()
    for i, materia in enumerate(materias):
        pos = i + 1
        print('%d - %s' % (pos, materia[0]))
        if count == pos:
            break


def mostrar_cursos(nome_materia, numero_curso=0):
    crawler = SESSION
    for i, curso in enumerate(crawler.cursos(nome_materia)):
        pos = i + 1
        if numero_curso:
            if numero_curso == pos:
                return curso[1]
        else:
            print('%d - %s' % (pos, curso[0]))


def mostrar_aulas(url_curso, numero_aula=0):
    crawler = SESSION
    aulas = crawler.aulas(url_curso)
    for i, aula in enumerate(reversed(list(aulas))):
        pos = i + 1
        if numero_aula:
            if numero_aula == pos:
                return aula['titulo_aula'], aula['data_aula'], aula['types']
        else:
            print('%d - %s' % (pos, aula['titulo_aula']))


def baixar_aula(titulo_aula, data_aula, type, path=''):
    crawler = SESSION
    for file in crawler.baixarAula(data_aula, type, path=path):
        p = (file[0] * 100) / file[1]
        sys.stdout.write('Baixando %s %s %.2f%% \r' % (type, titulo_aula, p))
        sys.stdout.flush()
    print('\n')


parser = argparse.ArgumentParser(
    description='cli para acesso ao Eu Vou Passar')
parser.add_argument('-c', '--cursos', metavar='materia', dest='nome_materia',
                    help='Mostra todos os cursos referentes a uma máteria')
parser.add_argument('-m', '--materias',
                    help='Mostra todas as matérias',
                    action='store_true')
parser.add_argument('-n', metavar='n', type=int,
                    help='número de matérias a serem mostrados')
parser.add_argument('-d', metavar='n', type=int, nargs='+',
                    help='download da aula')


args = parser.parse_args()
if args.materias:
    if args.n:
        mostrar_materias(args.n)
    else:
        mostrar_materias()
if args.nome_materia:
    if args.n:
        url_curso = mostrar_cursos(args.nome_materia, args.n)
        if args.d:
            for choose in args.d:
                titulo_aula, data_url, types = mostrar_aulas(url_curso, choose)
                for type in types:
                    if type:
                        baixar_aula(titulo_aula, data_url, type, path=PATH)
        else:
            mostrar_aulas(url_curso)
    else:
        mostrar_cursos(args.nome_materia)
