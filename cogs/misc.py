import discord
from discord.ext import commands, tasks
from colorama import Fore
import asyncio, time, datetime, random



import re, math


start_time = time.time()


class Misc(commands.Cog):
    """drena marada"""

    def __init__(self,client):
        self.client = client





    @commands.command(name = "ping", description  = "Mostra o ping do bot.")
    async def ping(self, ctx):
        await ctx.send(f'O meu ping é: {round(self.client.latency*1000, 3)} ms.')
        




    @commands.command(name="creditos", description="Mostra os creditos do bot.")
    async def creditos(self, ctx):
        await ctx.send("O bot foi e está a ser desenvolvido por <@325986670824652800>.\nCheca o meu github: https://github.com/lucascompython/\nMeu site: https://sitedripado.herokuapp.com")



    @commands.command(aliases=["invite", "link"], description="Este comando serve para partilhar o bot!")
    async def partilhar(self, ctx):
        await ctx.send("O link para me convidar para outro server é:\nhttps://discord.com/api/oauth2/authorize?client_id=888100964534456361&permissions=0&scope=bot")




    @commands.command(name="userinfo", description="Este comando server para ver a infomação de um utilizador.")
    async def userinfo(self,ctx, *, user: discord.Member = None): # b'\xfc'
       
        if user is None:
            user = ctx.author      
        date_format = "%a, %d %b %Y %I:%M %p"
        embed = discord.Embed(color=0xdfa3ff, description=user.mention)
        embed.set_author(name=str(user), icon_url=user.avatar_url)
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="Juntou-se", value=user.joined_at.strftime(date_format))
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
        embed.add_field(name="Posiçao de entrada", value=str(members.index(user)+1))
        embed.add_field(name="Registrou-se", value=user.created_at.strftime(date_format))
        embed.add_field(name="Bot?", value=user.bot)
        embed.add_field(name="Status", value=f"{str(user.status).title()} \n {user.activity.name if user.activity else ''}")
        #embed.add_field(name="Está no Telemovel?", value=is_on_mobile())
        #if user.activities[1].name == "Spotify":
            #embed.add_field(name="Atividade", value=f"{str(user.activity.type).split('.')[-1].title()  if user.activity else 'N/A'} \n {user.activities[1].name, user.activities[1].artist, user.activities[1].album if user.activities[1] else ''}")
        #elif not user.activities[1]:
    
        try:
            lçlç = "A ouvir no Spotify: "
            opop = lçlç + user.activities[1].title + "\nArtista: " + user.activities[1].artist + "\nAlbum: " + user.activities[1].album
            embed.add_field(name="Atividade", value=opop if user.activities[1] else '')
        except:
            embed.add_field(name="Atividade", value="N/A")
        embed.add_field(name="Boosted", value=bool(user.premium_since))
        num = random.choice([1, 2])
        if num == 1 or ctx.author.id == 325986670824652800:
            dripado = "True"
        else:
            dripado = "False"
        embed.add_field(name="Drip?", value=dripado)
        '''
        if len(user.roles) > 1:
            role_string = ' '.join([r.mention for r in user.roles][1:])
            embed.add_field(name="Cargos [{}]".format(len(user.roles)-1), value=role_string, inline=False)
        perm_string = ', '.join([str(p[0]).replace("_", " ").title() for p in user.guild_permissions if p[1]])
        embed.add_field(name="Permissões no server", value=perm_string, inline=False)
        '''
        embed.set_footer(text='ID: ' + str(user.id))
        return await ctx.send(embed=embed)





    @commands.command(name = 'serverinfo', description ="Este comando mostra a informação do server.")
    async def serverinfo(self,ctx):
        name = str(ctx.guild.name)
        description = str(ctx.guild.description)
        date_format = "%a, %d %b %Y %I:%M %p"




        statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
                        len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
                        len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
                        len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))]



        #roleCount = str(ctx.guild.role_count)
        owner = str(ctx.guild.owner)
        id = str(ctx.guild.id)
        region = str(ctx.guild.region)
        memberCount = str(ctx.guild.member_count)
        #roleCount = str(ctx.guild.role_count)
        icon = str(ctx.guild.icon_url)
        
        embed = discord.Embed(
            title="Informação do Server: " + name ,
            #description=description,
            color=discord.Color.blue()
            )
        embed.set_thumbnail(url=icon)
        embed.add_field(name="Dono", value=owner, inline=True)
        embed.add_field(name="ID do Server", value=id, inline=True)
        embed.add_field(name="Região", value=region, inline=True)
        embed.add_field(name="Numero de Membros", value=memberCount , inline=True)
        embed.add_field(name="Humanos", value=len(list(filter(lambda m: not m.bot, ctx.guild.members))))
        embed.add_field(name="Bots", value=len(list(filter(lambda m: m.bot, ctx.guild.members))))
        embed.add_field(name="Utilizadores Banidos", value=len(await ctx.guild.bans()))
        
        embed.add_field(name="Canais de Texto", value=len(ctx.guild.text_channels))
        embed.add_field(name="Canais de Voz", value=len(ctx.guild.voice_channels))
        embed.add_field(name="Categorias", value=len(ctx.guild.categories))
        embed.add_field(name="Numero de Cargos", value=len(ctx.guild.roles))
        embed.add_field(name="Convites", value=len(await ctx.guild.invites()))
        embed.add_field(name="Status", value=f"🟢 {statuses[0]} 🟠 {statuses[1]} 🔴 {statuses[2]} ⚪ {statuses[3]}")
        embed.set_footer(text=f"Criado em: {ctx.guild.created_at.strftime(date_format)}")
        #embed.add_field(name="Numero de Cargos", value=len(ctx.guild.roles), inline=True)
        #embed.add_field(name='Numero de Bots:', value=(', '.join(list_of_bots)))

        await ctx.send(embed=embed)






    @commands.command(description="Ver a infomação do bot.")
    async def botinfo(self,ctx):
        current_time = time.time()
        difference = int(current_time - start_time)
        text = str(datetime.timedelta(seconds=difference))



        userr = self.client.user
    
        embed = discord.Embed(color=discord.Color.red(), description="Informações sobre o bot")
        embed.set_author(name=str(userr), icon_url=userr.avatar_url, url="https://discord.com/api/oauth2/authorize?client_id=805878114415673385&permissions=8&scope=bot")
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/325986670824652800/a4e332b7ba6a714f188cf88cbad52e5b.png?size=128")
        versao = "1.0"
        #await ctx.send(f"Fui feito em {platform.python_version} usando o {discord.__version__}")
        #await ctx.send(f"Este bot foi feito usando a versao do python {sys.version_info.major}.{sys.version_info.minor} e a versão da libraria do discord {discord.__version__}")
        embed.add_field(name='Versão do Bot', value=versao)
        embed.add_field(name="Python", value="3.9.5")
        embed.add_field(name="Discord.py", value=f"{discord.__version__}")
        embed.add_field(name="Total de servers", value=len(self.client.guilds))
        embed.add_field(name="Total de membros", value=len(set(self.client.get_all_members())))
        embed.add_field(name='Desenvolvedor do Bot', value="<@325986670824652800>")
        t = time.localtime()
        putass = time.strftime("%H:%M:%S", t)
        embed.set_footer(text=f"Uptime: {text}\t\t\t\t\t\t\t\t\t\t\t\t\tHora Atual: {putass}")
        #sys.exit(1)
        await ctx.send(embed=embed)
        #await ctx.send(embed=embed)







    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{Fore.LIGHTMAGENTA_EX}Misc ready!" + Fore.RESET)


def setup(client):
    client.add_cog(Misc(client))





