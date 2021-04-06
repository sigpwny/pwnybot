# Required discord utility functions for adding / removing packages

def print_startup():
	print("################################")
	print("#                              #")
	print("#           pwnyBot            #")
	print("#    Discord Bot Aggregator    #")
	print("#      Created by SIGPwny      #")
	print("#                              #")
	print("################################")

def print_version():
	ver = open("version","r")
	f = ver.read().splitlines()
	ver.close()

	print("Version " + f[0].split("=")[1] + "." + f[1].split("=")[1] + "." + f[2].split("=")[1])

def load_token(path):
	f = open(path,"r")
	ret = f.read()
	f.close()

	return ret

def load_conf(path = './config/default.conf'):
	f = open(path,"r")
	ret = f.read().splitlines()
	f.close()

	return ret