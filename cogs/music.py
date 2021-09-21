import asyncio
import functools
import itertools
import math
import random
import DiscordUtils
import discord
import youtube_dl
from async_timeout import timeout
from discord.ext import commands
from pygicord import Paginator
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import psutil
import platform
from colorama import Fore
from disputils import BotEmbedPaginator, BotConfirmation, BotMultipleChoice
#import #
import json






youtube_dl.utils.bug_reports_message = lambda: ''


spotipy_id = "spotify client id here"
spotipy_secret = "spotify client secret here"
spotipy_id = spotipy_id.strip()
spotipy_secret = spotipy_secret.strip()


# with open(r"C:\Users\Utilizador\Desktop\BOTDODISCORD\cogs\SpotipyClientID.txt", "r") as scid:
#     spotipy_id = scid.read().strip()
#     scid.close()
# with open(r"C:\Users\Utilizador\Desktop\BOTDODISCORD\cogs\SpotipyClientSecret.txt", "r") as scs:
#     spotipy_secret = scs.read().strip()
#     scs.close()



sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=spotipy_id, client_secret=spotipy_secret))

class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass

class Utils():
    def getCurrentMemoryUsage(self):
        with open('/proc/self/status') as f:
            memusage = f.read().split('VmRSS:')[1].split('\n')[0][:-3]
            memusage = int(memusage)
            return memusage/1024
    def get_size(self, bytes, suffix="B"):
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f}{unit}{suffix}"
            bytes /= factor
class Spotify():
    def getTrackID(self, track):
        track = sp.track(track)
        return track["id"]
    def getPlaylistTrackIDs(self, playlist_id):
        ids = []
        playlist = sp.playlist(playlist_id)
        for item in playlist['tracks']['items']:
            track = item['track']
            ids.append(track['id'])
        return ids
    def getAlbum(self, album_id):
        album = sp.album_tracks(album_id)
        ids = []
        for item in album['items']:
            ids.append(item["id"])
        return ids
    def getTrackFeatures(self, id):
        meta = sp.track(id)
        features = sp.audio_features(id)
        name = meta['name']
        album = meta['album']['name']
        artist = meta['album']['artists'][0]['name']
        release_date = meta['album']['release_date']
        length = meta['duration_ms']
        popularity = meta['popularity']
        return f"{artist} - {album}"
    def getalbumID(self, id):
        return sp.album(id)

class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')

        #global puta
       # puta = data.get('view_count')
        self.views = data.get('view_count')

        #global merda
       # merda = data.get('like_count')
        self.likes = data.get('like_count')

        #global cona
        #cona = data.get('dislike_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** de **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Não foi possivel encontrar alguma coisa que corresponde com: `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Não foi possivel encontrar alguma coisa que corresponde com: `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Não foi possivel fetchar `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Não foi possivel encontrar alguma coisa que corresponde com: `{}`'.format(webpage_url))
        
        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @classmethod
    async def search_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        channel = ctx.channel
        loop = loop or asyncio.get_event_loop()

        cls.search_query = '%s%s:%s' % ('ytsearch', 10, ''.join(search))

        partial = functools.partial(cls.ytdl.extract_info, cls.search_query, download=False, process=False)
        info = await loop.run_in_executor(None, partial)

        cls.search = {}
        cls.search["title"] = f'Search results for:\n**{search}**'
        cls.search["type"] = 'rich'
        cls.search["color"] = 7506394
        cls.search["author"] = {'name': f'{ctx.author.name}', 'url': f'{ctx.author.avatar_url}', 'icon_url': f'{ctx.author.avatar_url}'}
        
        lst = []

        for e in info['entries']:
            #lst.append(f'`{info["entries"].index(e) + 1}.` {e.get("title")} **[{YTDLSource.parse_duration(int(e.get("duration")))}]**\n')
            VId = e.get('id')
            VUrl = 'https://www.youtube.com/watch?v=%s' % (VId)
            lst.append(f'`{info["entries"].index(e) + 1}.` [{e.get("title")}]({VUrl})\n')

        lst.append('\n**Type a number to make a choice, Type `cancel` to exit**')
        cls.search["description"] = "\n".join(lst)

        em = discord.Embed.from_dict(cls.search)
        await ctx.send(embed=em, delete_after=45.0)

        def check(msg):
            return msg.content.isdigit() == True and msg.channel == channel or msg.content == 'cancel' or msg.content == 'Cancel'
        
        try:
            m = await bot.wait_for('message', check=check, timeout=45.0)

        except asyncio.TimeoutError:
            rtrn = 'timeout'

        else:
            if m.content.isdigit() == True:
                sel = int(m.content)
                if 0 < sel <= 10:
                    for key, value in info.items():
                        if key == 'entries':
                            """data = value[sel - 1]"""
                            VId = value[sel - 1]['id']
                            VUrl = 'https://www.youtube.com/watch?v=%s' % (VId)
                            partial = functools.partial(cls.ytdl.extract_info, VUrl, download=False)
                            data = await loop.run_in_executor(None, partial)
                    rtrn = cls(ctx, discord.FFmpegPCMAudio(data['url'], **cls.FFMPEG_OPTIONS), data=data)
                else:
                    rtrn = 'sel_invalid'
            elif m.content == 'cancel':
                rtrn = 'cancel'
            else:
                rtrn = 'sel_invalid'
        
        return rtrn

    @staticmethod
    def parse_duration(duration: int):
        if duration > 0:
            minutes, seconds = divmod(duration, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)

            duration = []
            if days > 0:
                duration.append('{} dias'.format(days))
            if hours > 0:
                duration.append('{} horas'.format(hours))
            if minutes > 0:
                duration.append('{} minutos'.format(minutes))
            if seconds > 0:
                duration.append('{} segundos'.format(seconds))
            
            value = ', '.join(duration)
        
        elif duration == 0:
            value = "LIVE"
        
        return value


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester
    
    def create_embed(self):
        embed = discord.Embed(title='A tocar', description='```css\n{0.source.title}\n```'.format(self), color=discord.Color.green())
        embed.add_field(name='Duração', value=self.source.duration)
        #embed.add_field(name='Requisitada por', value=self.requester.mention)
        embed.add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
        embed.add_field(name='URL', value='[Click]({0.source.url})'.format(self))
        embed.add_field(name='Visualizações', value=self.source.views)#source
        embed.add_field(name='Likes', value=self.source.likes)#source
        embed.add_field(name='Dislikes', value=self.source.dislikes)#source
        embed.set_thumbnail(url=self.source.thumbnail)
        embed.set_author(name=f"Requisitado por {self.requester.name}", icon_url=self.requester.avatar_url)
        embed.set_footer(text=f"Upload date: {self.source.upload_date}")
        return embed

class SongQueue(asyncio.Queue):     
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self.exists = True

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()
            self.now = None

            if self.loop == False:
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with timeout(180):  # 3 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    self.exists = False
                    return
                
                self.current.source.volume = self._volume
                self.voice.play(self.current.source, after=self.play_next_song)
                await self.current.source.channel.send(embed=self.current.create_embed())
            
            #If the song is looped
            elif self.loop == True:
                self.now = discord.FFmpegPCMAudio(self.current.source.stream_url, **YTDLSource.FFMPEG_OPTIONS)
                self.voice.play(self.now, after=self.play_next_song)
            
            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


class Music(commands.Cog):

#    async def teardown(self):
#        try:
 #           await self.destroy()
 #       except KeyError:
 #           pass

 #   @commands.Cog.listener()
 #   async def on_voice_state_update(self, member, before, after):
 #       if not member.bot and after.channel is None:
  #          if not [m for m in before.channel.members if not m.bot]:
  #              await self.get_player(member.guild).teardown()


    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state or not state.exists:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('Este comando nao pode ser utilizado em canais privados(dm).')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('Um erro ocorreu: {}'.format(str(error)))

    @commands.command(name='join', invoke_without_subcommand=True, aliases=["entra", "connect"], description="Comando para fazer o bot entrar na tua sala.")
    async def _join(self, ctx: commands.Context):
        #
        #
        """Entra num canal de voz."""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            await ctx.send("Ja estou conectado numa sala otario.")
            return
        else:
            pass
        await ctx.send(f"Entrando em: {destination}")
        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='summon', description="Fazer o bot entrar numa sala de voz especificada.")
    @commands.has_permissions(manage_guild=True)
    async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        #
        #
        """Entra num canal de voz especifico.
        Se nenhum canal de voz foi especificado entra no seu.
        """

        if not channel and not ctx.author.voice:
            raise VoiceError('Ou tu nao tas num canal de voz ou nao especificaste um canal de voz.')
        
        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.send(f"Entrando em {destination}")
            await ctx.voice_state.voice.move_to(destination)
            return
        
        ctx.voice_state.voice = await destination.connect()
        await ctx.guild.change_voice_state(channel=destination, self_mute=False, self_deaf=True)
    @commands.command(name='leave', aliases=['disconnect', "sai"], description="Faz o bot sair da sala.")
    @commands.has_permissions(manage_guild=True)
    async def _leave(self, ctx: commands.Context):
        #
        #
        """Limpa a fila e sai do canal de voz."""

        if not ctx.voice_state.voice:
            return await ctx.send('Não estou conectado num canal de voz otario.')
        await ctx.send("Saindo...")
        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name='volume', aliases=["vol"], description="Muda o volume do bot.")
    async def _volume(self, ctx: commands.Context, *, volume: int):
        #
        #
        """Setar o volume do bot."""

        if not ctx.voice_state.is_playing:
            return await ctx.send('Não ah nenhum audio a ser tocado de momento.')

        if volume > 100 or volume < 0:
            return await ctx.send('O volume do bot deve ser entra 0 e 100')

        ctx.voice_state.current.source.volume = volume / 100
        await ctx.send('O volume do bot agora é: {}%'.format(volume))

    @commands.command(name='now', aliases=['current', 'playing',"np"], description="Mostra informação sovre a musica a ser tocada.")
    async def _now(self, ctx: commands.Context):
        #
        #
        """Mostra informa巽ão da musica que esta a ser tocada."""
        embed = ctx.voice_state.current.create_embed()
        await ctx.send(embed=embed)

    @commands.command(name='pause', aliases=['pa', "pausa"], description="Pausa a musica no bot.")
   #@commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        #
        #
        """Pausa o bot."""
        print(">>>Pause Command:")
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')
        else:
            await ctx.send("O bot ja esta pausado!")

    @commands.command(name='resume', aliases=['re', 'res'], description="Resuma a musica pausada no bot.")
   # @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context):
        #
        #
        """Resuma o bot."""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')
        else:
            await ctx.send("O bot ja esta resumado otario!")

    @commands.command(name='stop', description="Para a musica atual e limpa a fila.")
    @commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx: commands.Context):
        """Para o bot e limpa a fila."""
        #
        #
        ctx.voice_state.songs.clear()

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')
        else:
            await ctx.send("O bot ja ta stopado.")
    @commands.command(name='skip', aliases=['s', "next"], description="Avança para a proxima musica na fila.")
    async def _skip(self, ctx: commands.Context):
        """Vota pra dar skip.
        Seram presisos 3 votos para dar skip.
        """ 
        #
        #
        if not ctx.voice_state.is_playing:
            return await ctx.send('Não estou a tocar musica de momento...')

        voter = ctx.message.author
        if voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction('⏭')
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 0:
                await ctx.message.add_reaction('⏭')
                ctx.voice_state.skip()
            else:
                await ctx.send('Voto adicionaddo, currently at **{}/3**'.format(total_votes))

        else:
            await ctx.send('Otario, tu ja votaste.')

    @commands.command(name='queue', aliases=["q"], description="Mostra a fila.")
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """Mostra a fila.
        Para ja podes especificar a pagina da fila adicionando o numero da pagina no final do comando.
        """
        #
        #
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Fila vazia.')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)
        
        embed = (discord.Embed(description='**{} musicas:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='A ver a pagina: {}/{}'.format(page, pages)))
        #jiji = ctx.voice_state.songs
        #kaka = ["puta1", "puta2"]
        #global popo
        #popo = pages
        #paginator = Paginator(
            #page,pages,
            #pages=get_pages(jiji),
            #timeout=60.0,
            #has_input=False,
        #)
        #await paginator.start(ctx)
        
        await ctx.send(embed=embed)

    @commands.command(name='shuffle', aliases=["mix", "misturar"], description="Mistura a fila.")
    async def _shuffle(self, ctx: commands.Context):
        """Mistura a fila."""
        #
        #
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Fila vazia.')

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.command(name='remove' ,aliases=["remover"], description="Remove a musica selecionada da lista.")
    async def _remove(self, ctx: commands.Context, index: int):
        """Remove uma musica da fila."""
        #
        #
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Fila vazia.')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction('✅')

    @commands.command(name='loop', description="Da loop a fila.")
    async def _loop(self, ctx: commands.Context):
        """Da loop a musica que est叩 atualmente a ser tocada.
        Usa este comando outra vez para dar unloop.
        """
        #
        #
        if not ctx.voice_state.is_playing:
            return await ctx.send('Não est叩 nada a ser tocado de momento.')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.message.add_reaction('✅')

    @commands.command(name='play', aliases=['p'], description="Comando para por musica.")
    async def _play(self, ctx: commands.Context, *, search: str):
        # Checks if song is on spotify and then searches.
        """Comando para tocar musica, para ver os sites compativeis com o bot va a este site https://rg3.github.io/youtube-dl/supportedsites.html."""
        #
        #
        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)
        if "https://open.spotify.com/playlist/" in search or "spotify:playlist:" in search:
            async with ctx.typing():
                try:
                    trackcount = 0
                    process = await ctx.send(f"A processar. . .")
                    ids = Spotify.getPlaylistTrackIDs(self, search)
                    tracks = []
                    for i in range(len(ids)):
                        track = Spotify.getTrackFeatures(self, ids[i])
                        tracks.append(track)
                    for track in tracks:
                        trackcount += 1
                        try:
                            source = await YTDLSource.create_source(ctx, track, loop=self.bot.loop)
                        except YTDLError as e:
                            await ctx.send('Um erro ocorreu a tentar processar este pedido: {}'.format(str(e)))
                        else:
                            song = Song(source)
                            await ctx.voice_state.songs.put(song)
                except Exception as err:
                    await ctx.send("Erro!")
                    print(err)
        elif "https://open.spotify.com/album/" in search or "spotify:album:" in search:
            async with ctx.typing():
                process = await ctx.send(f"A processar. . .")
                try:
                    ids = Spotify.getAlbum(self, search)
                    tracks = []
                    for i in range(len(ids)):
                        track = Spotify.getTrackFeatures(self, ids[i])
                        tracks.append(track)
                    for track in tracks:
                        try:
                            source = await YTDLSource.create_source(ctx, track, loop=self.bot.loop)
                        except YTDLError as e:
                            await ctx.send('Um erro ocorreu a tentar processar este pedido: {}'.format(str(e)))
                        else:
                            song = Song(source)
                            await ctx.voice_state.songs.put(song)
                            await process.edit(content="Album obtido com sucesso.")
                except Exception as err:
                    await ctx.send("Erro!")
                    print(err)
        elif "https://open.spotify.com/track/" in search or "spotify:track:" in search:
            async with ctx.typing():
                process = await ctx.send(f"A processar. . .")
                try:
                    ID = Spotify.getTrackID(self, search)
                    track = Spotify.getTrackFeatures(self, ID)
                    source = await YTDLSource.create_source(ctx, track, loop=self.bot.loop)
                    song = Song(source)
                    await ctx.voice_state.songs.put(song)
                    await process.edit(content="Musica obtida com sucesso.")
                except Exception as err:
                    await ctx.send("Erro!")
                    print(err)
        
        elif "https://www.youtube.com/playlist" in search:

            async with ctx.typing():
                try:
                    source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
                except YTDLError as e:
                    await ctx.send('Um erro ocorreu a tentar processar este pedido: {}'.format(str(e)))
                else:
                    if not ctx.voice_state.voice:
                        await ctx.invoke(self._join)

                    song = Song(source)
                    #await ctx.voice_state.songs.put(song)
                    await ctx.send('Adicionado a fila: {}'.format(str(source)))

        else:
            async with ctx.typing():
                try:
                    source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
                except YTDLError as e:
                    await ctx.send('Um erro ocorreu a tentar processar este pedido: {}'.format(str(e)))
                else:
                    if not ctx.voice_state.voice:
                        await ctx.invoke(self._join)

                    song = Song(source)
                    await ctx.voice_state.songs.put(song)
                    await ctx.send('Adicionado a fila: {}'.format(str(source)))



    """
    @commands.command(name='search')
    async def _search(self, ctx: commands.Context, *, search: str):
        Searches youtube.
        It returns an imbed of the first 10 results collected from youtube.
        Then the user can choose one of the titles by typing a number
        in chat or they can cancel by typing "cancel" in chat.
        Each title in the list can be clicked as a link.
        async with ctx.typing():
            try:
                source = await YTDLSource.search_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
            else:
                if source == 'sel_invalid':
                    await ctx.send('Invalid selection')
                elif source == 'cancel':
                    await ctx.send(':white_check_mark:')
                elif source == 'timeout':
                    await ctx.send(':alarm_clock: **Time\'s up bud**')
                else:
                    if not ctx.voice_state.voice:
                        await ctx.invoke(self._join)
                    song = Song(source)
                    await ctx.voice_state.songs.put(song)
                    await ctx.send('Enqueued {}'.format(str(source)))
            """
    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('Não estas conectado a um canal de voz.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('O bot ja est叩 conectado a um canal de voz.')







 #   @commands.command()
 #   async def test(self, ctx):
 #       paginator = Paginator(
   #  #       pages=get_pages(),
     #       timeout=60.0,
      #      has_input=False,
      #  )
      #  await paginator.start(ctx)







    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{Fore.CYAN}Music ready!" + Fore.RESET)


def get_pages(puta):
    pages = []
    for i in range(page, popo):
        embed = discord.Embed()
        embed.title = f"I'm the embed {i}!"
        pages.append(embed)
    return pages
#embed.description = '**{} musicas:**\n\n{}'.format(len(puta), puta).set_footer(text='A ver a pagina: {}/{}'.format(pagee, pagess))






def setup(client):
    client.add_cog(Music(client))

