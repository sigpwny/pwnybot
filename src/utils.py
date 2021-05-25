import yaml
import os
# This is the universal prefix that all bots must use.
# The prefix of each package is then added on to 
UNIVERSAL_PREFIX = '!'


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

def load_conf(conf = 'default'):
	f = open('./config/loaders/' + conf + '.conf',"r")
	ret = f.read().splitlines()
	f.close()

	return ret

def gen_prefdict():
	with open('./config/bot_pfx.yml','r') as file:
		pref_dloc = yaml.safe_load(file)
	return dict((v,k) for k,v in pref_dloc.items())

def gen_cogdict(bot):
	if cog_dict_g != {}:
		return cog_dict_g.copy()
	else:
		for cog in bot.cogs:
			print(cog)
		return {}
	
pref_dict = gen_prefdict()
cog_dict_g = {}
def get_prefix(bot, message):
	cog_dict = gen_cogdict(bot)
	if message.content[0] != UNIVERSAL_PREFIX or not '-' in message.content:
		return ['\x00'] # If its not formatted properly, return an impossible character for normal people to send. TODO permission checking just to be safe

	ret = []
	prefix = message.content.split('-')[0][1:]
	command = message.content.split('-')[1]
	c_name = pref_dict[prefix]

	print(pref_dict,prefix,command,c_name)
	
	if prefix in pref_dict:
		return [UNIVERSAL_PREFIX + prefix + '-']
	return ['\x00']

