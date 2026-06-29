def set_settings():
	with open("./settings.csv", 'r') as file:
		data = file.read()
	lines = data.split("\n")
	data = {}
	for line in lines:
		if line == "": continue
		line = line.split(',')
		key, value = line[:2]
		if "%" in value:
			value = value.replace("%", "")
			value = float(value) / 100
		else:
			value = int(value)
		data[key] = value

	settings = {}
	settings["KILL_ASSIST_POINTS"] = data["Kill Assist Points"]
	settings["MAX_VIBRATION"]      = data["Max Vibration"]
	settings["MIN_VIBRATION"]      = data["Min Vibration"]
	settings["SCORE_DECAY"]        = data["Score Decay"]
	settings["MONITOR"]            = data["Monitor"]
	settings["DEBUG"]              = (data["Debug"] == 1)
	settings["MANUAL_DELAY"]       = float(data["Manual Delay"])

	for key in settings.keys():
		assert settings[key] != None
	
	return settings
