#!/bin/python

import sys, re

from patterns import *
from pprint import pprint

def get_lines(file):
	file.seek(0,2)
	while True:
		line = file.readline()
		if line == None:
			time.sleep(0.25)
			continue
		yield line

print(searches)
def get_event_type(line: str) -> str:
	line = line.strip()
	# if re.search("vmdl", line)
	# if re.search("vmdl", line) != None: print(f" -------- {line} --------")
	for event in searches.keys():
		search = f".*?{searches[event]}"
		if re.match(search, line) != None:
			print(event)
			return f"{event}"
	return None

def get_event_score(event_type: str, score: int) -> float:
	if event_type not in points.keys(): return score
	foo = points[event_type]
	operation = foo[0]
	count = float(foo[1:])

	if operation == '+': score = score + count
	if operation == '-': score = score - count
	if operation == '*': score = score * count
	if operation == '/': score = score / count

	return score

def parse_line(line: str) -> dict:
	data = {}
	split = line.split()

	if line == None: return None
	if split == []: return None
	if len(split) < 3: return None

	mdate = split[0]
	mtime = split[1]

	try:
		lbracket = line.index('[')
		rbracket = line.index(']')
		mtype = line[lbracket + 1 : rbracket]
		mcontent	= line[rbracket + 2 : ]
	except:
		mtype = split[2]
		mcontent = "".join(split[3:])

	data["date"] = mdate
	data["time"] = mtime
	data["type"] = mtype
	data["content"] = mcontent

	if mtype == "Killer":
		data["Killer"] = mcontent.split(',')[0]
		data["Dying"] = mcontent.split(',')[1].replace("Dying:", "")
		data["Assisters"] = mcontent.split(',')[2].replace("NumberofAssisters:","")
		print(f"{data["Killer"]} killed {data["Dying"]} with {data["Assisters"]} Players")

	if mtype == "Player":
		data["Kills"] = mcontent.split(',')[2].replace("Hero:","")

	if mtype == "Bullet":
		if "player" in mcontent:
			print("Shot Player")
		elif "npc_neutral_hideout_cat" in mcontent:
			print("Shot Hideout Cat")
		elif "npc_neutral_flying_pigeon" in mcontent:
			print("Shot Hideout Bird")
		else:
			print("Shot Box?")

	return data

ignored_message_types = [
	"",
	"writesteamremotestoragefileasync",
	"client",
	"rendersystem",
	"soundsystemlowlevel",
	"created",
	"splitscreen",
	"source2shutdown",
	"shutdownsource2logging",
	"createcitadelbot",
	"initializing",
	"bullet",
	"has",
	"resourcesystem",
	"vprof",
	"a",
	"attempting"
	"prediction",
	"navmesh",
	"animation 2",
	"inputsystem",
	"cannot",
	"steamnetsockets",
	"idle",
	"failed",
	"frame",
	"avg",
	"performant",
	"usually",
	"****",
	"panorama",
	"job",
	"particles",
	"server",
	"node",
	"casyncwriteinprogressoncomplete(",
	"getsessionconnectioninfo",
	"cgameparticlemanagersetparticlecontrolent",
	"gcclient",
	"writesteamremotestoragefileasync(",
	"socache",
	"localization system"
]

if __name__ == "__main__":
	path = "/home/samuel/.local/share/Steam/steamapps/common/Deadlock/game/citadel/console.log"

	console_log = open(path, 'r')
	message_log = open("./message_log", 'w')

	message_types = set()
	data = []

	print("Testing Parser")

	lines = get_lines(console_log)
	# lines = file.read().split("\n")
	state = None
	is_comeback = False
	gametime = 0


	for line in lines:
		try: message = parse_line(line)
		except: continue

		event_type = get_event_type(line)
		if event_type != None:
			print(event_type) 

		if message == None: continue

		mtype = message["type"]
		content = message["content"]
		
		if mtype in [None, ""]: continue
		if mtype == "ChangeGameState": state = content
		if mtype == "Comeback": is_comback = (content == "Inactive")
		if mtype == "GameTime": gametime = float(content.split(',')[0])

		message["state"] = state

		message_types.add(message["type"])
		data.append(message)

		with open(f"./messages/{mtype}", 'w') as file:
				print(line, file=file)
		
		# if mtype.lower() in ignored_message_types: continue
		# pprint(line)

	message_types = set([x.replace(" ", "_") for x in message_types])

	with open("./message_types", 'w') as file:
		pprint(message_types, stream=file)

	for mtype in message_types:
		matching_messages = [x for x in data if x["type"] == mtype]

	print("Finished Parsing File")

	console_log.close()
	sys.exit(0)
