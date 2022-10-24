from mcdreforged.api.all import *
import time
import os
import collections

class Config(Serializable):
	changeTime: int = 10
	scoreboardList: list[str] = [
		'death'
	]

config: Config
configFile = os.path.join('config','ScoreboardTimer.json')
index = 0
isWorking = 0

def changeScoreboard(server: ServerInterface):
	global index
	if(index>=len(config.scoreboardList)):
		index = 0
	server.execute(f"scoreboard objectives setdisplay sidebar {config.scoreboardList[index]}")
	index = index+1

@new_thread('ScoreboardTimerThread')
def run(server: ServerInterface):
	global isWorking
	isWorking = 1
	while isWorking == 1:
		changeScoreboard(server)
		time.sleep(config.changeTime)

def showScoreboardList(src: CommandSource):
	src.reply('当前的计分板有')
	for i in config.scoreboardList:
		src.reply(i)

def showHelpMessage(src: CommandSource):
	src.reply('§e==========ScoreboardTimer==========§r')
	src.reply('§b使用!!st start开始计分板轮换§r')
	src.reply('§b使用!!st stop停止计分板轮换§r')
	src.reply('§b使用!!st set <time>修改计分板轮换时间§r')
	src.reply('§b使用!!st add <name>增加一个计分板§r')
	showScoreboardList(src)

def startWork(src: CommandSource):
	if isWorking == 1:
		src.reply('计分板已经在轮换！')
	else:
		src.reply('计分板开始轮换~')
		run(src.get_server())

def stopWork(src: CommandSource):
	global isWorking
	src.reply('正在停止计分板轮换')
	isWorking = 0

def setChangeTime(src: CommandSource,context: dict):
	cgtime = context['changeTime']
	src.reply(f'计分板轮换时间由{config.changeTime}修改为{cgtime}')
	config.changeTime=context['changeTime']

def addScoreboard(src: CommandSource,context: dict):
	config.scoreboardList.append(context['name'])
	showScoreboardList(src)

def on_load(server: PluginServerInterface, old):
	global config
	config = server.load_config_simple(file_name=configFile, in_data_folder=False, target_class=Config)
	server.register_help_message('!!st', '定时更换计分板')
	server.register_command(\
			Literal('!!st').runs(showHelpMessage)\
			.then(Literal('start').runs(startWork))\
			.then(Literal('stop').runs(stopWork))\
			.then(Literal('set').then(Integer('changeTime').runs(setChangeTime).at_min(1).requires(lambda src: src.has_permission(2))))
			.then(Literal('add').then(Text('name').runs(addScoreboard).requires(lambda src: src.has_permission(2))))
		)

def on_unload(server: PluginServerInterface):
	global isWorking
	isWorking = 0
	server.save_config_simple(config,file_name=configFile, in_data_folder=False)