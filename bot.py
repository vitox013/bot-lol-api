import time
import requests
from lcu_driver import Connector
import GUI as GUI
import urllib3
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
connector = Connector()

gameMode = GUI.choices()
inGame = False
ban = GUI.escolhas['ban']
picks1 = [GUI.escolhas['opcao1'],GUI.escolhas['opcao2']]
picks = [x.lower() for x in picks1]


@connector.ready
async def connect(connection):
    global championsMap, summonerId 
    tempChampionsMap = {}
    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    summonerJson = await summoner.json()
    summonerId = summonerJson['summonerId']
    championList = await connection.request('get', f'/lol-champions/v1/inventories/{summonerId}/champions-minimal')
    championListJson = await championList.json()
    for i in range(len(championListJson)):
        tempChampionsMap.update({championListJson[i]['name']: championListJson[i]['id']})
    championsMap = dict((k.lower(), v) for k,v in tempChampionsMap.items())
    

@connector.ready
async def inLobby(connection):
    try:
        lobby = await connection.request('get', '/lol-lobby/v2/lobby')
        lobbyJson = await lobby.json()
        if lobbyJson['message']:
            print('Não está no lobby')
            await connection.request('post', '/lol-lobby/v2/lobby', data={"queueId":gameMode})
            print('Lobby criado')
    except(Exception,):
        print('Já está no saguão')

@connector.ready
async def waitingRoles(connection):
    rolesReady = False
    print('Aguardando lanes serem selecionadas')
    while not rolesReady:
      lobby = await connection.request('get', '/lol-lobby/v2/lobby')
      lobbyJson = await lobby.json()
      if lobbyJson['localMember']['firstPositionPreference'] != 'UNSELECTED' and lobbyJson['localMember']['secondPositionPreference'] != 'UNSELECTED':
        print('Lanes foram selecionadas')
        rolesReady = True

@connector.ready
async def startQueue(connection):
    await connection.request('post', '/lol-lobby/v2/lobby/matchmaking/search', data={})

@connector.ws.register('/lol-matchmaking/v1/ready-check', event_types=('UPDATE',))
async def checkStart(connection, event):
    if event.data['state'] == 'InProgress' and event.data['playerResponse'] == 'None':
        await connection.request('post', '/lol-matchmaking/v1/ready-check/accept', data={})

@connector.ws.register('/lol-champ-select/v1/session', event_types=('CREATE', 'UPDATE'))
async def champSelect(connection,event):
    global inGame
    i = 0
    j = 0
    banning = False
    picking = False
    prePicked = False
    preSel = False
    phase = ''
    lobbyPhase = event.data['timer']['phase']
    localPlayerId = event.data['localPlayerCellId']

    for act in event.data['actions']:
      for actArray in act:
        if actArray['actorCellId'] == localPlayerId and actArray['isInProgress'] == True:
          phase = actArray['type']
          actId = actArray['id']
          if phase == 'ban':
            banning = actArray['isInProgress']
          elif phase == 'pick':
            picking = actArray['isInProgress']
    if phase == 'pick' and lobbyPhase == "PLANNING" and not preSel:
      while not preSel:
        try:
          await connection.request('patch', '/lol-champ-select/v1/session/actions/%d' % actId, data={"championId":championsMap[picks[0]], "completed": True})
          preSel = True
        except(Exception,):
          print('Tentando pré selecionar')
    if phase == 'ban' and lobbyPhase == 'BAN_PICK' and banning:
      while banning:
        try:
          await connection.request('patch', '/lol-champ-select/v1/session/actions/%d' % actId, data={"championId":championsMap[ban], "completed": True} )
          banning = False
        except(Exception,):
          if i > len(ban):
            i = 0
    if phase == 'pick' and lobbyPhase == "BAN_PICK" and picking:
      while picking:
        try:
          await connection.request('patch', '/lol-champ-select/v1/session/actions/%d' % actId, data={"championId":championsMap[picks[j]], "completed": True})
          j += 1
          picking = False
        except(Exception,):
          j += 1
          if j > len(picks):
            j = 0
    if lobbyPhase == 'PLANNING' and not prePicked:
      try:
          await connection.request('patch', '/lol-champ-select/v1/session/actions/%d' % actId, data={"championId": championsMap['Teemo'], "completed": False})
          prePicked = True
      except(Exception,):
          print(Exception)
    if lobbyPhase == 'FINALIZATION':
      while not inGame:
        try:
          requestGameData = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False)
          gameData = requestGameData.json()['gameData']['gameTime']
          if gameData > 0 and not inGame:
            print('Entrei no if')
            inGame = True
            sys.exit()
          time.sleep(2)
        except (Exception,):
            print('Waiting for game to start...')
            time.sleep(2)

@connector.close
async def disconnect(connection):
    print('The client has been closed!')
    await connector.stop()

connector.start()






