import sys, time, asyncio

from math import cos
from asyncio import Lock, run
from threading import Thread
from multiprocessing import Process
from time import sleep

import buttplug
from buttplug import (
	ButtplugClient, 
	ButtplugError,
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

async def check_battery(device) -> int:
	if device.has_input(InputType.BATTERY):
		battery = await device.battery()
		print(f"Battery: {battery * 100:.0f}%")
	return 0

def set_events(client):
	""" Sets Buttplug.io Events """
	client.on_device_added = lambda d: print(f"Connected: {d.name}")
	client.on_device_removed = lambda d: print(f"Disconnected: {d.name}")
	client.on_scanning_finished = lambda: print("Scan complete")
	client.on_server_disconnect = lambda: print("Server disconnected!")

async def set_vibration(device) -> float:
	last_checked = 0
	interval = 1
	while (True):
		print("\tStart of Loop")
		now = int(time.time())
		print("\t1")
		if now + interval > last_checked:
			async with max_lock:
				maximum = max_vibe
		base = (0.5) * (cos(now) + 1.0)
		vibration = round(maximum * base, 2)
		print("\t2")
		print(f"\t v = {vibration:.2f}")
		# if device.has_output(OutputType.VIBRATE):
		# device.run_output(DeviceOutputCommand(OutputType.VIBRATE, vibration))
		try:
			await device.run_output(DeviceOutputCommand(OutputType.VIBRATE, vibration))
		except:
			raise Exception("Error")
		print("\t3")
		await asyncio.sleep(1)
		print("\tEnd of Loop")
	return

def set_vibration_loop(device) -> None:
	# if device == None: return
	# TODO spawn vibe pattern thread
	print("Starting Vibration Loop")
	while(True):
		run(set_vibration(device))
		sleep(0.1)
	print("End of Vibe Loop")

async def test_device(device) -> None:
	print("  Starting vibration at 25%...")
	await device.run_output(DeviceOutputCommand(OutputType.VIBRATE, 0.25))
	await asyncio.sleep(1)

	print("  Increasing to 50%...")
	await device.run_output(DeviceOutputCommand(OutputType.VIBRATE, 0.5))
	await asyncio.sleep(1)

	print("  Full power (100%)...")
	await device.run_output(DeviceOutputCommand(OutputType.VIBRATE, 1.0))
	await asyncio.sleep(1)

	print("  Zero power (0%)...")
	await device.run_output(DeviceOutputCommand(OutputType.VIBRATE, 0.0))
	await asyncio.sleep(1)

max_lock = Lock()
max_vibe = 0.5

class Vibrator:
	maximum = 0.0
	max_lock = None
	vibration = 0
	client = None
	device = None
	vibe_process = None

	@classmethod
	async def initialize(self):
		global max_lock
		global max_vibe
		print("Initializing Vibrator Object")
		self.vibration = 0
		self.client = ButtplugClient("Pluglocked")
		await connect(self.client)
		set_events(self.client)
		self.device = await get_device(self.client)
		if self.device != None:
			await ping(self.device)
			await check_battery(self.device)
		loop = set_vibration_loop
		# self.vibe_process = Thread(target=loop, args=(self.device,)).start()
		sleep(0.1)
		print("Vibrator Object Ready")
		print(f"Max Vibe = {max_vibe}")
	
	@classmethod
	async def set_max(self, maximum: float) -> None:
		global max_lock
		global max_vibe
		assert type(maximum) is float
		assert 0 <= maximum <= 1, f"Vibration {vibration} outside bounds"
		async with max_lock:
			max_vibe = maximum
		if self.device == None: return
		if self.device.has_output(OutputType.VIBRATE):
			await self.device.run_output(DeviceOutputCommand(OutputType.VIBRATE, max_vibe))
		return

	@classmethod
	async def disconnect(self) -> int:
		if self.client.connected:
			await self.client.disconnect()
			print("Disconnected.")
		return 0
