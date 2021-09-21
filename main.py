#!/usr/bin/env python

import discord
from discord.ext import commands, tasks
import json, os






prefixes = ""
def get_prefix(client, message):
    with open("./prefixes.json", "r") as f:
        global prefixes
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]





intents = discord.Intents().all()
client = commands.Bot(command_prefix = get_prefix, intents=intents, case_insensitive=True, description="L33t Bot", owner_id= 325986670824652800, strip_after_prefix=True, help_command=None)




for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")




@client.event
async def on_ready():
    print("tou pronto")




@client.event
async def on_command_error(ctx, error):
    
    #await ctx.send(error)



    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Por favor escreva todos os argumentos.')

    if isinstance(error, commands.MemberNotFound):
        await ctx.send('Membro não encontrado.')

    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Comando não existe.\nPara mais informação sobre os comandos use "help".')
    
    if isinstance(error, commands.BotMissingAnyRole):
        await ctx.send('Não tenho permissões para tal coisa.')

    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send('Não tenho permissões para tal coisa.')

    if isinstance(error, commands.BotMissingRole):
        await ctx.send('Não tenho permissões para tal coisa.')

    if isinstance(error, commands.MissingPermissions):
        await ctx.send('Não tem permissões para tal coisa.')

    if isinstance(error, commands.BadArgument):
        await ctx.send('Argumento invalido.')

    if isinstance(error, commands.NSFWChannelRequired):
        await ctx.send("Este canal não é NSFW!")

    #elif isinstance(error, commmands)


    client.remove_command("help")

    @client.command(description="Comando de ajuda")
    async def help(ctx, cog="1"):
        embed = discord.Embed(
              title="Comando de Ajuda!")
           
        embed.set_thumbnail(url=ctx.author.avatar_url)
        cogs = [c for c in client.cogs.keys()]
        cogs.remove("Mensagem")
        for cog in cogs:
            commandList = ""
            for command in client.get_cog(cog).walk_commands():
                if command.hidden:
                    continue

                commandList += f"**{command.name}** - *{command.description}*\n"

            commandList += "\n\n\n"

            embed.add_field(name=cog, value=commandList, inline=False)


        await ctx.send(embed=embed)






@client.event
async def on_guild_join(guild):
    

    print(f"O bot entrou em: {guild}")
    
    with open('./prefixes.json', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(guild.id)] = '.'

    with open('./prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    
@client.event
async def on_guild_remove(guild):
    print(f"O bot saio de: {guild}")
    with open('./prefixes.json', 'r') as f:
        prefixes = json.load(f)
    
    prefixes.pop(str(guild.id))

    with open('./prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)


#mudar o prefixo
@client.command(help = "Este comando serve para mudar o prefixo do bot neste se!rver.")
async def changeprefix(ctx, prefix):
    with open('./prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open('./prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)  

    await ctx.send(f'Prefixo mudado para: **{prefix}**')




client.run("TOKEN HERE", reconnect=True)
