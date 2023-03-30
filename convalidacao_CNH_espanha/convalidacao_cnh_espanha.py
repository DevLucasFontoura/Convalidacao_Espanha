#!/usr/bin/env python
# coding: utf-8

# ##INSTALANDO BIBLIOTECAS NECESSÁRIAS

# In[ ]:


#!sudo apt-get install tesseract-ocr tesseract-ocr-por
#get_ipython().system('pip install opencv-python ')
#get_ipython().system('pip install pytesseract')
#get_ipython().system('pip install pyautogui')
#get_ipython().system('pip install pygetwindow')


# In[1]:


import re
import os
import io
import json
import base64
import uuid
import shutil
import chardet
import pandas as pd
import nest_asyncio
nest_asyncio.apply()
from time import sleep
from datetime import datetime

# import requests
from google.cloud import vision
import pytesseract
import cv2
import glob
import pyautogui
import pygetwindow as gw
from selenium.webdriver.common.by import By
from selenium import webdriver


# In[62]:

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'convalidacao-cnh-23e2836c50f0.json'
PASTA_ARQUIVOS_TXT = 'w:\\CGSIE\\CONVALIDACAO_CNH\\txt\\'
PASTA_ARQUIVOS_PROCESSADOS = 'w:\\CGSIE\\CONVALIDACAO_CNH\\processados\\'
# PASTA_ARQUIVOS_TXT = 'C:\\Automacao\\Convalidacao_CNH\\TXT\\'
# PASTA_ARQUIVOS_HOD = '/content/drive/MyDrive/Ministério da Infraestrutura/Convalidacao_de_CNH/HOD/'
PASTA_TEMP = 'C:\\Users\\Administrador\\HODObjs\\'
PASTA_ARQUIVOS_HOD = 'C:\\Automacao\\Convalidacao_CNH\\HOD\\'
PASTA_ELEMENTOS_TELA = PASTA_ARQUIVOS_HOD + 'elementos_tela\\'
ARQUIVO_CONTROLE = '/content/drive/MyDrive/Ministério da Infraestrutura/Convalidacao_de_CNH/controle.json'
ARQUIVO_MUNICIPIOS = 'C:\\Automacao\\Convalidacao_CNH\\siconv-cnh\\siconv-cnh\\upload\\scripts\\municipios.csv'
BASE_CAPTCHA = 'C:\\Automacao\\Convalidacao_CNH\\imagens\\captcha\\' 
EXTENSAO_TXT = '.txt'
EXTENSAO_IMG = '.png'
KEY_NOME = 'NOME'
KEY_DT_NASC = 'DT.NASC'
KEY_SEXO = 'SEXO'
KEY_MUNIC = 'COD.MUN'
KEY_UF = 'UF'
KEY_PRIMEIRA_HABLT = 'PRIM.HABIL'
KEY_ULTIMA_EMISSAO = 'ULT.EMISS.HISTORICO'
KEY_CATEGORIA = 'CATEGORIA'
KEY_VALIDADE_CNH = 'VALIDADE'
KEY_RESTRICOES = 'IMPEDIMENTOS/LIBERACOES'
KEY_USUARIO_ENCONTRADO = 'REC FOUND'
KEY_USUARIO_NAO_ENCONTRADO = 'NOT FOUND'
LB_TOXICOLOGICO = 'AE'
LB_USUARIO_INEXISTENTE = '(016)'
LB_MENU_SISTEMAS = 'MENU DE SISTEMAS'
LB_CODIGO = 'CODIGO'
LB_NETNAME = 'ULTIMO ACESSO'
LB_TELA = 'TELA 002'
LB_RENACH = 'RENACH'
LB_SESSAO_EXPIRADA = 'TEMPO LIMITE PARA ESTABELECIMENTO DE SESSAO ESGOTADO'
LB_ENCERRAR_BROWSER_1 = 'Favor encerrar o browser'
LB_ENCERRAR_BROWSER_2 = 'Favor encerrar o brouser'
LB_ENCERRAR_BROWSER_3 = 'Codigo de retorno invalido'
FILENAME1 = 'dados_cadastrais'
FILENAME2 = 'ultima_emissao'
FILENAME3 = 'historicos'
CMD = 'Administrador: Prompt de Comando'
APP_HOD = 'Terminal 3270 - A'
APP_CONTROL_PANEL = 'Painel de Controle'
WD_ON_DEMAND = 'Host On-Demand'
URL_HOD ='https://hod.serpro.gov.br/'
HOD_FILE = 'hodcivws.jsp'
ESPACO_TOTAL_CATEGORIAS = 173 - 77
ESPACO_BRANCO_NOT_FOUND = 128

# NÃO ALTERAR, POSIÇÃO DA VARIÁVEL NO ARQUIVO
CATEGORIAS = (
    ('A', 1), 
    ('AB', 2), 
    ('B', 1),
    ('C', 2),
    ('AC', 3), 
    ('D', 3),
    ('AD', 4),
    ('E', 3), 
    ('BE', 1), 
    ('CE', 1), 
    ('DE', 1),
    ('AE', 4),
    ('X', 8))
DF_MUNICIPIOS = None

def carregarMunicipios():
    global DF_MUNICIPIOS
    DF_MUNICIPIOS = pd.read_csv(ARQUIVO_MUNICIPIOS, encoding='latin-1', sep=';')

def getArquivosPastaTXT():
  lista_arquivos = glob.glob(PASTA_ARQUIVOS_TXT + "*.txt")
  lista_arquivos = [arquivo.split('/')[-1][:-4] for arquivo in lista_arquivos]
  return lista_arquivos

def getDataAtual():
    data_hora_atual = datetime.now()
    return data_hora_atual.strftime('"%m/%d/%Y, %H:%M:%S"')

def listarArquivosNaoProcessados():
  lista_processados = listarArquivosProcessados()
  todos_arquivos = getArquivosPastaTXT()
  nao_processados = set(todos_arquivos) - set(lista_processados)
  return nao_processados

def listarArquivosProcessados():
  
  with open(ARQUIVO_CONTROLE) as json_file:
    dict_arquivos_processados = dict()
    
    try:
      dict_arquivos_processados = json.load(json_file);
      lista = list(dict_arquivos_processados.keys()) 
    except Exception:
      print("Arquivo de controle vazio!!!")
      lista = []

  return lista

def getGrayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

def lerImagemHOD(caminho_imagem: str):
    # extrairInformacoesVisionAPI(caminho_imagem)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    imagem = cv2.imread(caminho_imagem)
    dim = redimensionarImagem(imagem.shape[1], imagem.shape[0], taxa=1)
    imagem = cv2.resize(imagem, dim, interpolation = cv2.INTER_AREA) 
    gray_image = getGrayscale(imagem)
    threshold_img = thresholding(gray_image)
    texto = pytesseract.image_to_string(threshold_img, lang="por")
    texto = limparTexto(texto)
    return texto

def extrairInformacoesVisionAPI(caminho_arquivo):
    client = vision.ImageAnnotatorClient()
    
    with io.open(caminho_arquivo, 'rb') as image_file:
        content = image_file.read()
    
    imagem = vision.Image(content=content)
    response = client.text_detection(image=imagem)
    texts = response.text_annotations
    print(texts)

    if response.error.message:
        raise Exception('Erro ao extrair dados do documento!')

def redimensionarImagem(largura: int, altura: int, taxa=0.15) -> tuple:
    largura +=  (largura * taxa)
    altura += (altura * taxa)
    return (int(largura), int(altura))


def limparTexto(texto):
    texto = list(filter(lambda linha: linha.strip(), texto.splitlines()))
    return texto


def verificarExisteTela(caminho_arquivo, tela):
    dc = lerArquivo(caminho_arquivo)
    return list(filter(lambda item: tela in item, dc))

def verificarEncoding(arquivo: str) -> str:
    try:
        with open(arquivo, 'rb') as file:
            rawdata = file.read()
        sleep(3)
        resultado = chardet.detect(rawdata)
        encoding = resultado['encoding']
    except Exception as ex:
        print('OCORREU UM ERRO AO IDENTIFICAR A CODIFICAÇÃO')
    else:
        return encoding
    finally:
        file.close()

def lerArquivo(arquivo: str, encoding='utf8'):
    try:
        encoding = verificarEncoding(arquivo)
        with open(arquivo, encoding=encoding) as file:
            linhas = [line for line in file.readlines() if line.strip()]
        sleep(3)
    except Exception as ex:
        print(ex)
        print(f'Falha ao ler arquivo {arquivo}')
    else:
        return linhas
    finally:
        file.close()

def getInstanciaWD():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    instancia = webdriver.Chrome('C:\\Users\\Administrador\\Downloads\\chromedriver_win32\\chromedriver.exe', options=options)
    return instancia

def abrirPaginaWebHOD(navegador):
    pagina = navegador.get(URL_HOD)
    return pagina


def localizarElementoTela(elemento, centro=False):
    coordenadas = tuple()
    if centro:
        coordenadas = pyautogui.locateCenterOnScreen(elemento)
    else:
        coordenadas = pyautogui.locateOnScreen(elemento)
    sleep(3)
    return coordenadas


def clicarCentroTela():
    largura, altura = pyautogui.size()
    sleep(2)
    pyautogui.click(largura/2, altura/2)


def aguardarJanelaAtiva(janela, timer=0):
    aplicacoes = gw.getAllTitles()
    i = 0
    while janela not in aplicacoes:
        sleep(1)
        aplicacoes = gw.getAllTitles()
        i += 1
        if timer != 0 and i == timer:
            break


def fecharJanelaAtiva(janela):
    sleep(2)
    app = gw.getWindowsWithTitle(janela)[0]
    app.close()


def verificarHODAbertoSemErro():
    sleep(5)
    hod = gw.getWindowsWithTitle(APP_HOD)[0]
    hod.restore()
    hod.activate()
    hod.maximize()
    sleep(5)
    salvarTela(f'{PASTA_ARQUIVOS_HOD}temp.png')
    sleep(4)
    dc = lerImagemHOD(f'{PASTA_ARQUIVOS_HOD}temp.png')
    sleep(6)
    return (len(list(filter(lambda item: LB_TELA in item or LB_MENU_SISTEMAS in item or LB_RENACH in item, dc))) > 0)


def executarHOD():
    pyautogui.press('winleft')
    sleep(2)
    pyautogui.write('cmd')
    sleep(2)
    pyautogui.press('enter')
    sleep(2)
    pyautogui.write(f'javaws C:\Automacao\Convalidacao_CNH\HOD\{HOD_FILE}')
    sleep(2)
    pyautogui.press('enter')
    sleep(2)
    fecharJanelaAtiva(CMD)
    aguardarJanelaAtiva(WD_ON_DEMAND, timer=5)
    pyautogui.press('enter')
    sleep(2)
    pyautogui.press('enter')
    aguardarJanelaAtiva(APP_HOD, timer=6)
    sleep(90)
    try:
        if verificarHODAbertoSemErro(): 
            pyautogui.write('RENACH')
            sleep(2)
            pyautogui.press('enter')
            sleep(2)
            pyautogui.press('down', presses=2) # CADASTRO
            pyautogui.press('enter')
            sleep(2)
            pyautogui.press('enter') # BINCO
            sleep(2)
        else:
            print('NÃO ACESSOU')
            fecharJanelaAtiva(APP_HOD)
            fecharJanelaAtiva(APP_CONTROL_PANEL)
            raise Exception('SESSÃO EXPIRADA NO HOD')
    except IndexError:
        raise Exception('Arquivo hodcivws.jsp não localizado. Favor realizar upload do arquivo antes de executar o script.')
    except Exception as ex:
        raise Exception(ex)

def salvarTela(caminho_arquivo):
    pyautogui.screenshot(caminho_arquivo, region=(390, 190, 1150, 770))


def criarPastaUsuario(numero_registro):
    PASTA_USUARIO = getPastaUsuario(numero_registro)
    os.mkdir(PASTA_USUARIO)
    return PASTA_USUARIO


def getPastaUsuario(numero_registro):
    pasta_usuario = f'{PASTA_ARQUIVOS_HOD + numero_registro}\\'
    return pasta_usuario


def consultarCondutorRENACH(numero_registro):
    pasta_usuario = criarPastaUsuario(numero_registro)
    pyautogui.write(numero_registro)
    sleep(2)
    pyautogui.press('enter')
    sleep(3)
    salvarDadosTela(FILENAME1)
    # pyautogui.press('enter') 
    caminho_arquivo = f'{PASTA_TEMP + FILENAME1 + EXTENSAO_TXT}'
    if verificarExisteTela(caminho_arquivo, LB_USUARIO_INEXISTENTE):
        print('USUÁRIO NÃO EXISTE')
        pyautogui.press('F3')
        sleep(2) 
        pyautogui.press('enter') # BINCO
        return None
    else:
        print('USUÁRIO EXISTE')
        pyautogui.press('F9')
        sleep(2)
        salvarDadosTela(FILENAME3)
        pyautogui.press('F3', presses=3)
        sleep(2)
        pyautogui.press('down', presses=2)
        sleep(2)
        pyautogui.press('enter')
        sleep(2)
        pyautogui.write(numero_registro)
        sleep(2)
        pyautogui.press('enter')
        sleep(2)
        salvarDadosTela(FILENAME2)
        sleep(2)
        moverParaPastaUsuario(pasta_usuario)
        sleep(7)
        pyautogui.press('F3', presses=2)
        sleep(2)
        pyautogui.press('enter')
            
    return numero_registro

def moverParaPastaUsuario(pasta_usuario):
    os.rename(PASTA_TEMP + FILENAME1 + EXTENSAO_TXT, pasta_usuario + FILENAME1 + EXTENSAO_TXT)
    os.rename(PASTA_TEMP + FILENAME2 + EXTENSAO_TXT, pasta_usuario + FILENAME2 + EXTENSAO_TXT)
    os.rename(PASTA_TEMP + FILENAME3 + EXTENSAO_TXT, pasta_usuario + FILENAME3 + EXTENSAO_TXT)

def salvarDadosTela(nome_arquivo):
    tamanho_tela = pyautogui.size()
    sleep(2)
    _x, _y = tamanho_tela[0]/2, tamanho_tela[1]/2
    _y_enviar_area_rascunho = _y + 140
    sleep(2)
    pyautogui.moveTo(x=_x, y=_y)
    sleep(2)
    pyautogui.click()
    sleep(2)
    pyautogui.rightClick(duration=1)
    sleep(2)
    pyautogui.moveTo(x=_x, y=_y_enviar_area_rascunho)
    sleep(2)
    pyautogui.click()
    sleep(2)
    pyautogui.click(x=1621, y=996)
    sleep(2)
    pyautogui.click(x=807, y=607)
    sleep(2)
    pyautogui.write(nome_arquivo)
    sleep(2)
    pyautogui.press('enter')
    sleep(2)
    pyautogui.click(x=1688, y=992)
    sleep(2)
    pyautogui.hotkey('alt', 'e')
    sleep(2)
    pyautogui.hotkey('alt', 'a')
    sleep(2)
    pyautogui.hotkey('alt', 'r')
    sleep(2)
    pyautogui.click()

def getDadosBasicos(arquivo):
    print('DADOS BÁSICOS')
    nome = getDado(arquivo, KEY_NOME)
    dt_nasc = getDado(arquivo, KEY_DT_NASC)
    categoria = getDado(arquivo, KEY_CATEGORIA)
    validade_cnh = getDado(arquivo, KEY_VALIDADE_CNH)
    # sexo =  getDado(arquivo, KEY_SEXO)[2]
    # cod_municipio = getDado(arquivo, KEY_MUNIC)
    # municipio, cod_ibge = getMunicipio(cod_municipio)
    # uf_end = getDado(arquivo, KEY_UF)
    return nome.strip(), dt_nasc.strip(), categoria.strip(), validade_cnh.strip()

def getUltimaEmissao(arquivo):
    print('DADOS DA ÚLTIMA EMISSÃO DE CNH')
    dados = lerArquivo(arquivo)
    linha_encontrada = dados[5]
    print(linha_encontrada)
    ult_emissao = linha_encontrada.split()[5]
    print(ult_emissao)
    return ult_emissao.strip()

def verificarUsuario(arquivo, data_validade):
    print('VERIFICAR USUÁRIO COM RESTRIÇÕES OU CNH EXPIRADA')
    retorno = False
    try:
        restricoes = getDado(arquivo, KEY_RESTRICOES)
        sem_restricoes = KEY_RESTRICOES in restricoes
        data_atual = datetime.now()
        data_validade = datetime.strptime(data_validade, r'%d/%m/%Y')
        retorno = sem_restricoes and (data_validade > data_atual)
    except:
        print('USUÁRIO COM RESTRIÇÕES')
        return retorno
    finally:
        return retorno

def getDado(caminho_arquivo, campo):
    campos = {KEY_NOME: 1, KEY_DT_NASC: 1, KEY_SEXO: 3, KEY_PRIMEIRA_HABLT: 1, KEY_MUNIC: 1, KEY_UF: 2, KEY_CATEGORIA: 1, KEY_VALIDADE_CNH: 4, KEY_RESTRICOES: 1}
    indice_campo = campos[campo]
    dados = lerArquivo(caminho_arquivo)
    linha_encontrada = list(filter(lambda item: campo in item, dados))[0]
    dado = linha_encontrada.split(':')[indice_campo]
    if campo == KEY_DT_NASC or campo == KEY_UF or campo == KEY_MUNIC or campo == KEY_CATEGORIA:
        dado = dado.split()[0]
    return dado.strip()

def getMunicipio(codigo):
    codigo = int(codigo.lstrip('0'))
    municipio, cod_ibge = DF_MUNICIPIOS[DF_MUNICIPIOS['CÓDIGO DO MUNICÍPIO - TOM'] == codigo][['MUNICÍPIO - IBGE','CÓDIGO DO MUNICÍPIO - IBGE']].values[0]
    return municipio, cod_ibge     

def getNomeSobrenome(nome_completo):
    nome_slicing = nome_completo.split()
    return nome_slicing[0].strip(), ' '.join([partes_sobrenome for partes_sobrenome in nome_slicing[1:]]).strip()

def formatarData(data):
    return ''.join([elemento for elemento in data.split('/')[::-1]])

def getTamanhoEspacoEmBranco(posicao):
    return posicao[1] - posicao[0]

def formatarLinha(registro, nome, nome_restante, data_nasc, data_categoria, categoria, usuario):
    primeiro_nome = (12, 28)
    sobrenome = (28, 68)
    if usuario == KEY_USUARIO_NAO_ENCONTRADO:
        categoria_formatada = ' ' * ESPACO_BRANCO_NOT_FOUND
    else:
        categoria_formatada = formatarCategoria(data_categoria, categoria)
    return f'D{registro}{nome.rjust(getTamanhoEspacoEmBranco(primeiro_nome))}{nome_restante.rjust(getTamanhoEspacoEmBranco(sobrenome))}{data_nasc}{categoria_formatada}{usuario}'

def formatarCategoria(data, categoria):  
    tamanho_data = len(data)
    total_espacos_brancos = ESPACO_TOTAL_CATEGORIAS - tamanho_data

    if categoria.upper().strip() == 'A' or categoria.upper().strip() == 'AB' or categoria.upper().strip() == 'AC' or categoria.upper().strip() == 'AD':
        data = data + (total_espacos_brancos * ' ') + (32 * ' ')
        return data
    elif categoria.upper().strip() == 'B'or categoria.upper().strip() == 'C' or categoria.upper().strip() == 'D':
        data = (16 * ' ') + data + (total_espacos_brancos * ' ') + (16 * ' ')
        return data
    elif categoria.upper().strip() == 'E':
        data = (16 * ' ') + data + (16 * ' ') + data[-16:] + (32 * ' ')
        return data
    elif categoria.upper().strip() == 'AE':
        return data + (16 * ' ') + data[-16:] + (32 * ' ')
    else:
        return None

def apagarArquivo(caminho_arquivo):
    os.remove(caminho_arquivo)
    sleep(2)

def apagarArquivos(temp_files_path):
    for raiz, pastas, arquivos in os.walk(temp_files_path, topdown=True):

        for arquivo in arquivos:
            os.remove(f'{raiz}\\{arquivo}')
        
        for pasta in pastas:
            shutil.rmtree(f'{raiz}\\{pasta}')

def salvarArquivoHOD(arquivo):
    novo_arquivo = PASTA_ARQUIVOS_HOD + HOD_FILE
    with open(novo_arquivo, 'wb') as f:
        f.write(arquivo.read())
        f.close()


def escreverArquivo(caminho_arquivo_txt, caminho_arquivo_processado, dados):
    linhas = lerArquivo(caminho_arquivo_txt)
    primeira_linha = linhas[0].rstrip()
    ultima_linha = linhas[-1].rstrip()
    linhas_escrever = [primeira_linha]

    for linha in linhas[1:-1]:
        registro = linha[1:12]
        try: 
            nome_completo = dados[registro][KEY_NOME]
            nome, sobrenome = getNomeSobrenome(nome_completo)
            data_nasc = formatarData(dados[registro][KEY_DT_NASC])
            ultima_emissao = formatarData(dados[registro][KEY_ULTIMA_EMISSAO])
            validade_cnh = formatarData(dados[registro][KEY_VALIDADE_CNH])
            categoria = formatarData(dados[registro][KEY_CATEGORIA])
            categoria_filtrada = filter(lambda c: c[0] == categoria.upper(), CATEGORIAS)
            fator_multiplicador = list(categoria_filtrada)[0][1]
            datas_formatadas = (ultima_emissao + validade_cnh) * fator_multiplicador
            usuario = KEY_USUARIO_ENCONTRADO if dados[registro][KEY_USUARIO_ENCONTRADO] else KEY_USUARIO_NAO_ENCONTRADO
            linhas_escrever.append(formatarLinha(registro, nome, sobrenome, data_nasc, datas_formatadas, categoria.upper(), usuario))
        except KeyError:
            tamanho_linha = len(linha.strip())
            not_found = KEY_USUARIO_NAO_ENCONTRADO
            not_found = not_found.rjust(getTamanhoEspacoEmBranco((tamanho_linha, 213)))
            linhas_escrever.append(f'{linha.strip()}{not_found}') 
        except IndexError as ier:
            print('ERRO NO CONDUTOR:', registro)
            raise Exception('ERRO AO ESCREVER ARQUIVO!!!')
    
    linhas_escrever.append(ultima_linha)
        
    with open(caminho_arquivo_processado, 'x') as file:
        file.write('\n'.join(linhas_escrever))


def main():
    print('SCRIPT INICIALIZADO:' + getDataAtual())

    carregarMunicipios()

    try:
        print('ABRIR O HOD')    
        executarHOD()
        print('HOD ABERTO')
    except Exception as ex:    
        raise Exception(ex)
    else:
        arquivos_leitura = set(os.listdir(PASTA_ARQUIVOS_TXT))
        arquivos_processados = set(os.listdir(PASTA_ARQUIVOS_PROCESSADOS)) 
        arquivos = list(arquivos_leitura - arquivos_processados)
        for arquivo in arquivos:
            print('LER ARQUIVO') 
            linhas = lerArquivo(PASTA_ARQUIVOS_TXT + arquivo)
            print('ARQUIVO LIDO')
            registros = [linha[1:12] for linha in linhas[1: -1]]
            print('CONSULTAR CONDUTORES')

            for registro in registros:
                consultarCondutorRENACH(registro)
            
            print('CONDUTORES CONSULTADOS')
            dados = dict()

            print('FORMATAR DADOS DO USUÁRIO')
            for registro in registros:
                try:
                    pasta = getPastaUsuario(registro)
                    print(pasta)
                    nome, data_nasc, categoria, data_validade = getDadosBasicos(pasta + FILENAME1 + EXTENSAO_TXT)
                    print(nome, data_nasc, categoria, data_validade)
                    data_ult_emissao = getUltimaEmissao(pasta + FILENAME2 + EXTENSAO_TXT)
                    print(data_ult_emissao)
                    usuario_encontrado = verificarUsuario(pasta + FILENAME3 + EXTENSAO_TXT, data_validade)
                    print(usuario_encontrado)
                    dados[registro] = {KEY_NOME: nome, KEY_DT_NASC: data_nasc, KEY_CATEGORIA: categoria, KEY_ULTIMA_EMISSAO: data_ult_emissao, KEY_VALIDADE_CNH: data_validade, KEY_USUARIO_ENCONTRADO: usuario_encontrado}
                except Exception as ex:
                    print('ERRO GENÉRICO!!!!', ex)
                    raise Exception(ex)
            print('REGISTROS FORMATADOS')

            print('ESCREVENDO NO ARQUIVO')
            escreverArquivo(PASTA_ARQUIVOS_TXT + arquivo, PASTA_ARQUIVOS_PROCESSADOS + arquivo, dados)

        apagarArquivos(PASTA_ARQUIVOS_TXT)
        print('SCRIPT FINALIZADO: ' + getDataAtual())
    finally:
        fecharJanelaAtiva(APP_HOD)
        fecharJanelaAtiva(APP_CONTROL_PANEL)
        apagarArquivos(PASTA_ARQUIVOS_HOD)

# def efetuarLogin(pagina, usuario, senha):
#     input_usuario = pagina.find_element(by=By.ID, value='login_user')
#     sleep(1)
#     input_senha = pagina.find_element(by=By.ID, value='login_password')
#     sleep(1)
#     input_usuario.send_keys(usuario)
#     input_senha.send_keys(senha)
#     # LER CAPTCHA KKKKKKKKKKKKKKKKKKK
#     bt_login = pagina.find_eleme
#     nt(by=By.ID, value='login_button')
#     bt_login.click()


# def lerImagemCaptcha():
#     #img_captcha = pagina.find_element(by=By.ID, value='img_captcha_serpro_gov_br')
#     from pytesseract import image_to_string
#     img = cv2.imread(r'C:\Users\Administrador\Downloads\captcha.png')
#     gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     (h, w) = gry.shape[:2]
#     gry = cv2.resize(gry, (w*2, h*2))
#     cls = cv2.morphologyEx(gry, cv2.MORPH_CLOSE, None)
#     thr = cv2.threshold(cls, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
#     pytesseract.pytesseract.tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#     txt = image_to_string(thr)
#     print(txt)


# def criarBaseTreinamento(pagina):
#     baixarImagemCaptcha(pagina)
#     for _ in range(990):
#         bt_atualizar_captcha = pagina.find_element(by=By.ID, value='btnRecarregar_captcha_serpro_gov_br')
#         sleep(1)
#         bt_atualizar_captcha.click()
#         baixarImagemCaptcha(pagina)


# def baixarImagemCaptcha(pagina):
#     try:
#         with open(BASE_CAPTCHA + str(uuid.uuid4()) + EXTENSAO_IMG, 'wb') as file:
#             img_captcha = pagina.find_element(by=By.ID, value='img_captcha_serpro_gov_br')
#             img_src = img_captcha.get_attribute("src")
#             base64string = re.sub(r"^.*?/.*?,", "", img_src)
#             image_as_bytes = str.encode(base64string)  # convert string to bytes
#             recovered_img = base64.b64decode(image_as_bytes)  # decode base64string
#             file.write(recovered_img)
#             file.close()
#     except Exception as ex:
#         print(ex)

# navegador = getInstanciaWD()
# abrirPaginaHOD(navegador)
# sleep(5)
# # criarBaseTreinamento(navegador)

# nao_processados = listarArquivosNaoProcessados()
# print(nao_processados)

# navegador = getInstanciaWD()
# pagina = abrirPaginaHOD(navegador)
# efetuarLogin(pagina, )

# for arquivo in nao_processados:
#   lerArquivoTXTCNH(arquivo)


# arquivo_txt_cnh = lerArquivoTXTCNH

