import interactions
from interactions import Extension, SlashContext

from lib.util import command, subcommand

import csv
import os
import random

filepath = os.path.dirname(os.path.abspath(__file__)) + "/copypasta.csv"

class copypasta(Extension):

    def __init__(self,bot):
        self.id_lst = []
        self.name_lst = []
        self.pasta_lst = []
        with open(filepath) as csvfile:
            reader = csv.reader(csvfile)
            row = next(reader)
            for row in reader:
                self.id_lst.append(row[0])
                self.name_lst.append(row[1])
                self.pasta_lst.append(row[2])
        print(self.name_lst)
            

    @subcommand(id={'description': "copypasta id"})
    async def byid(self, ctx: SlashContext, id: int) -> None:
        """copypasta by id"""
        for exist_id in self.id_lst:
            if int(exist_id) == id:
                await ctx.send(self.pasta_lst[self.id_lst.index(str(id))])
                return
        await ctx.send("Not Found")




    @subcommand(name={'description': "copypasta name","autocomplete" : True})
    async def byname(self, ctx: SlashContext, name: str) -> None:
        """copypasta by name"""
        for exist_name in self.name_lst:
            if exist_name == name:
                await ctx.send(self.pasta_lst[self.name_lst.index(name)])
                return
        await ctx.send("Not Found")

    @byname.autocomplete("name")
    async def find_name(self, ctx: interactions.AutocompleteContext):
        '''Autocomplete that provides challenge categories for chal create'''
        current = ctx.kwargs.get("name")
        new_lst = []
        for exist_name in self.name_lst:
            if current in exist_name:
                new_lst.append(exist_name)
        await ctx.send(new_lst[:25])

    @subcommand()
    async def random(self, ctx: SlashContext) -> None:
        """random copypasta"""
        await ctx.send(random.choice(self.pasta_lst))
