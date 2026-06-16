#!/bin/python

import sys, os
import pathlib
import time, datetime
import asyncio

from math import floor

from parse_log import *

from buttplug import (
	ButtplugClient, 
	DeviceOutputCommand, 
	InputType,
	OutputType
)

async def connect(client) -> int:
	try:
		print("Connecting to server ...")
		await client.connect("ws://127.0.0.1:12345")
		print(f"Connected to: {client.server_name}")
		print("Connection successful")

	except ButtplugError as e:
		print(f"Failed to connect: {e}")
		return 1

	return 0

async def disconnect(client) -> int:
	if client.connected:
		await client.disconnect()
		print("Disconnected.")
	return 0

async def get_device(client):
	device = None
	
	print("Finding Devices ...")

	devices_found = len(client.devices.values())

	if devices_found == 0:
		print("No Connected Devices, Scanning ...")
		await client.start_scanning()
		await asyncio.sleep(5)  # Wait for devices to be found
		await client.stop_scanning()
		devices_found = len(client.devices.values())

	if devices_found == 0:
		print("No Devices Connected, Please Connect Device")
		return None

	if devices_found == 1:
		for device in client.devices.values():
			print(f"Found: {device.name}")
			continue

	if devices_found > 1:
		print(f"No Multi-Toy Support")
		raise Exception(f"No Multitoy support: Expected 1 toy found: {client.devices.values()}")

	return device

async def ping(device) -> int:
	""" Checks for Devices and Gives a Buzz to indicate connection"""
	print("Pinging Device ...")

	if device.has_output(OutputType.VIBRATE):
		await device.run_output(DeviceOutputCommand(OutputType.VIBRATE, 0.05))
		await asyncio.sleep(0.25)
		await device.stop()

	print("Ping Successful")
	return 0

async def set_events(client) -> None:
	""" Sets Buttplug.io Events """
	client.on_device_added = lambda d: print(f"Connected: {d.name}")
	client.on_device_removed = lambda d: print(f"Disconnected: {d.name}")
	client.on_scanning_finished = lambda: print("Scan complete")
	client.on_server_disconnect = lambda: print("Server disconnected!")

async def set_vibration(device, vibration) -> None:
	assert type(vibration) is float
	await device.run_output(DeviceOutputCommand(OutputType.VIBRATE, vibration))
	return

async def check_battery(device) -> int:
	if device.has_input(InputType.BATTERY):
		battery = await device.battery()
		print(f"Battery: {battery * 100:.0f}%")
	return 0

async def main():

	home = pathlib.Path.home()
	deadlock_path = f"{home}/.local/share/Steam/steamapps/common/Deadlock/game/citadel"
	filepath = f"{deadlock_path}/console.log"

	vibration = float(0)

	client = ButtplugClient("Pluglocked")

	await connect(client)
	await set_events(client)
	device = await get_device(client)

	if device != None:
		await ping(device)
		await check_battery(device)

	log = open(filepath)

	last_update = datetime.datetime.now()
	lines = get_lines(log)

	last_time = 0
	print_period = 0.5

	for line in lines:
		print(line)
		epoch = time.time()
		event_type = get_event_type(line)
		vibration = get_event_score(event_type, vibration)
		await set_vibration(device, vibration)
		if floor(epoch) > last_time + print_period: 
			print(vibration)
			last_time = epoch
		

	await disconnect(client)

if __name__ == "__main__":
	asyncio.run(main())
	sys.exit()
