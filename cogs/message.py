import discord
from discord.ext import commands, tasks
from colorama import Fore
from main import get_prefix



class Mensagem(commands.Cog):
	"""drena marada"""

	def __init__(self,client):
		self.client = client




	@commands.Cog.listener()
	async def on_message(self, message):
		if self.client.user.mentioned_in(message):
			await message.channel.send(f"O meu prefixo é: {get_prefix(self.client, message)}")






	@commands.Cog.listener()
	async def on_ready(self):
		print(f"{Fore.RED}Message ready!" + Fore.RESET)





def setup(client):
	client.add_cog(Mensagem(client))





