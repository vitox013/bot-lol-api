from os import listdir
import pyautogui
import time
import PySimpleGUI as sg
import sys
import webbrowser
import pygetwindow

url = 'https://github.com/vitox013'

def janelaInicial():
    sg.theme("DarkBlue")
    layout = [
        [sg.Text('Bot criado por viteeera (GitHub)', tooltip=url, enable_events=True,key=f'URL {url}', font=("Arial", 11, "underline"))],
        [sg.Image('imgs/okTeemo.png')],
        [sg.Text('Vá lá buscar seu café que eu aceito a fila')]
    ]
    return sg.Window('Queue Acceptor', layout, finalize=True,size=(360, 260), location=(2, 300),element_padding=20, font=("Arial", 11), element_justification='c', icon=r'imgs/botIcon.ico')

def janelaChampions():
    sg.theme("DarkBlue")
    layout = [
        [sg.Column([[sg.Text('Selecione modo de jogo', font=('Arial',16, 'underline'),key='msgModo')]], visible=True,key='msgGrandeModo')],
        [sg.Radio('Escolha alternada', 'modosDeJogo', disabled=False,key='escolhaAlternada', pad=((0,5),0))],
        [sg.Radio('Ranqueada solo/duo', 'modosDeJogo',disabled=False, key='soloDuo',pad=((13,0),0))],
        [sg.Radio('Ranqueada flexível', 'modosDeJogo',disabled=False, key='flex')],
        [sg.Text("Primeira opção de campeão:")],
        [sg.Input(key='opcao1')],
        [sg.Text("Segunda opção de campeão(caso 1° seja banido):")],
        [sg.Input(key='opcao2')],
        [sg.Text("Banir quem?")],
        [sg.Input(key='ban')],
        [sg.Column([[sg.Button('Iniciar BOT', font="Arial, 11", bind_return_key=True, visible=True,pad=(0, 10))]], justification='center')]
    ]

    return sg.Window('Informe os Campeões', layout, finalize=True,  location=(2, 300), font=("Arial", 11), margins=(10, 20),icon=r'imgs/botIcon.ico',element_justification='c')


# ======================= FUNCÕES GENERICAS =================================
def removeSuffix(inputString, suffix):
    if suffix and inputString.endswith(suffix):
        return inputString[:-len(suffix)]
    return inputString

def loadImages(dirPath='./imgs/'):
    fileNames = listdir(dirPath)
    targets = {}

    for file in fileNames:
        path = 'imgs/' + file
        targets[removeSuffix(file, '.png')] = path
    return targets

def eventListenerFecharJogo():
    global event
    if event == sg.WIN_CLOSED or event == 'Parar Bot':
        sys.exit()

# ======================= FUNÇÕES BOT RODANDO =================================
def championChoices():
    global window, event, values, janela1, imagens
    while event != 'Iniciar BOT':
        window,event,values = sg.read_all_windows()
        escolhas = values
        eventListenerFecharJogo()
        return escolhas

def readWindows():
    global window, event, values
    window, event, values = sg.read_all_windows(timeout=1)

def choices():
    global escolhas
    if escolhas['flex']:
        return 440
    elif escolhas['escolhaAlternada']:
        return 400
    else: 
        return 420
    
def windows():
    global imagens, janela3,janela1,escolhas,window,values,event

    imagens = loadImages()
    janela3 = janelaInicial()
    window, event, values = sg.read_all_windows(timeout=5000)
    if event == sg.WINDOW_CLOSED:
        sys.exit()
    elif event.startswith("URL "):
        webbrowser.open(url)
    janela3.close()
    janela1 = janelaChampions()
    escolhas = championChoices()
    janela1.close()

windows()