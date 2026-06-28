import sys, subprocess

# windows
# py -m venv venv
# venv\Scripts\activate

# linux
# python3 -m venv venv
# source venv/bin/activate

# subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'my_package'])

if __name__ == "__main__":
	subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', './requirements.txt'])




