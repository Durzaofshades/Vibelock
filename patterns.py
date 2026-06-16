
print("Loading Settings")

searches = {
	"Build": r"(Build:)/s",
	"Server Number": r"(Server Number)",
	"Game State Change": r"(OnGameStateChanged)",
	"Kill": r"(Killer:)",
	"Time": r"(GameTime:)",
	"Silver Wolf": r"werewolf_transform.vmdl",
	"Silver Human": r"werewolf.vmdl",
	"Player Model Loaded": "vmdl",
}

points = {
	"Kill":         "+0.100,",
	"Time":         "*0.99",
	"Silver Wolf":  "+0.500",
	"Silver Human": "-0.300"
}

