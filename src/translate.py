import os

''' Translates single entity discord bots using discord.py into cogs usable by pwnyBot '''

def translate(path):
    try:
        f = open(path,'r')
    except Exception as e:
        print("Translate Hit An Exception:" + e)
    
    f = f.read()
    

def main():
    print("Translate time")

if __name__ == '__main__':
    main()