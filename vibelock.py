#!./env/bin/python

import sys, os
import pathlib
import time, datetime
import asyncio

from settings import *
from math import floor

from screen_capture import Kill_Log
# from parse_log import *
from vibe import Vibrator

SETTINGS = set_settings()
DEBUG = SETTINGS["DEBUG"]

# KILL_ASSIST_POINTS = None
# MAX_VIBRATION      = None
# MIN_VIBRATION      = None
# SCORE_DECAY        = None
# MONITOR            = None

async def get_events(logs: list[asyncio.Queue]) -> list[str]:
	events = []
	for log in logs:
		event = log.get()
		assert type(event) is str
		events.append(event)
	if DEBUG:
		print(events)
	return events

last_update = time.time()
def update_vibration(vibration: float, events: list[str]) -> int:
	assert type(vibration) is float
	global last_update
	now = time.time()
	time_elapsed = now - last_update
	last_vibration = vibration
	if DEBUG: print(events)
	for event in events:
		# -- Kills --
		if "Kills" in event: 
			# Kills = {x}
			try:
				kills = float(event.split("=")[-1].strip())
			except:
				kstring = event.split(",")[0]
				kills = float(kstring.split("=")[-1].strip())
			if kills > 0:
				vibration = vibration + SETTINGS["KILL_ASSIST_POINTS"]
		vibration = min(SETTINGS["MAX_VIBRATION"], vibration)
		# -- Time Passed --
		vibration = max(SETTINGS["MIN_VIBRATION"], vibration - (time_elapsed * SETTINGS["SCORE_DECAY"]))
	last_update = now
	if DEBUG: print(f"Vibration changed by {vibration - last_vibration:.2f}")
	return vibration

async def main():

	home = pathlib.Path.home()
	deadlock_path = f"{home}/.local/share/Steam/steamapps/common/Deadlock/game/citadel"
	filepath = f"{deadlock_path}/console.log"

	global DEBUG
	DEBUG = False
	if "--debug" in sys.argv:
		DEBUG = True
	
	global SETTINGS

	vibe = Vibrator()
	await vibe.initialize()

	# Open Kill Logger
	kills = Kill_Log(SETTINGS, Debug = DEBUG)
	kill_queue = kills.queue

	logs = [kill_queue]

	now = time.time()
	last_time = 0
	print_period = 0.5

	starting_vibration = 0.05
	vibration = starting_vibration

	while(True):
	# for i in range(3):
		epoch = time.time()
		events = await get_events(logs)
		# print(events)
		vibration = update_vibration(vibration, events)
		await vibe.set_max(vibration)
		print(f"Max Vibration = {vibration:.2f}")
		# print(f"Current Vibration = {vibe.vibration:.2f}")

	await vibe.disconnect()
	return

if __name__ == "__main__":
	asyncio.run(main())
	sys.exit()
