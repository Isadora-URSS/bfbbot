import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from servidor import manter_ativo

import aiohttp
import os
import asyncio
import re
import random
from socket import gethostname

load_dotenv()

class botãocargo(discord.ui.Button):
    def __init__(self, cargo_id, custom_id, style, emoji, label):
        super().__init__(custom_id = custom_id, style = style, emoji = emoji, label = label)
        self.cargo = cargo_id

    async def callback(self, interação):
        cargo = interação.guild.get_role(self.cargo)
        membro = interação.user
        if not isinstance(membro, discord.Member):
            membro = interação.guild.get_member(interação.user_id)
        if cargo not in membro.roles:
            try:
                await membro.add_roles(cargo)
            except:
                await interação.response.send_message("Não foi possível adicionar o cargo, tente de novo.", ephemeral = True)
            else:
                await interação.response.send_message("Cargo adicionado \U0001f44d", ephemeral = True)
        elif cargo in membro.roles:
            try:
                await membro.remove_roles(cargo)
            except:
                await interação.response.send_message("Não foi remover o cargo, tente de novo.", ephemeral = True)
            else:
                await interação.response.send_message("Cargo removido \U0001f44d", ephemeral = True)

class botãocargoexclusivo(discord.ui.Button):
    def __init__(self, cargo_id, custom_id, style, emoji, label):
        super().__init__(custom_id = custom_id, style = style, emoji = emoji, label = label)
        self.cargo = cargo_id

    async def callback(self, interação):
        cargo = interação.guild.get_role(self.cargo)
        membro = interação.user
        if not isinstance(membro, discord.Member):
            membro = interação.guild.get_member(interação.user_id)
        outros_cargos = self.view.lista_cargos.copy()
        outros_cargos.remove(self.cargo)
        if cargo not in membro.roles:
            if any([cargo in outros_cargos for cargo in [cargo.id for cargo in membro.roles]]):
                await interação.response.send_message("Remova seu cargo de cor atual antes de de trocar por outro.", ephemeral = True)
            else:
                try:
                    await membro.add_roles(cargo)
                except:
                    await interação.response.send_message("Não foi possível adicionar o cargo, tente de novo.", ephemeral = True)
                else:
                    await interação.response.send_message("Cargo adicionado \U0001f44d", ephemeral = True)
        elif cargo in membro.roles:
            try:
                await membro.remove_roles(cargo)
            except:
                await interação.response.send_message("Não foi remover o cargo, tente de novo.", ephemeral = True)
            else:
                await interação.response.send_message("Cargo removido \U0001f44d", ephemeral = True)

class viewcargos(discord.ui.View):
    def __init__(self, botões):
        super().__init__(timeout = None)
        for botão in botões:
            self.add_item(botão)

class viewcargosexclusivos(discord.ui.View):
    def __init__(self, botões):
        super().__init__(timeout = None)
        for botão in botões:
            self.add_item(botão)
        self.lista_cargos = [botão.cargo for botão in self.children]

botões_rpg = (
    botãocargo(768110565545345036, "BFB2012BOT:ParticipanteDoRpg", discord.ButtonStyle.blurple, None, "Obter acesso"),
)
botões_twitter = (
    botãocargo(812109324457345025, "BFB2012BOT:Twitter:PerfilAdms", discord.ButtonStyle.gray, os.getenv("emoji_adm"), None),
    botãocargo(816835654763544596, "BFB2012BOT:Twitter:PerfilJP", discord.ButtonStyle.gray, os.getenv("emoji_jp"), None),
    botãocargo(816835503382331463, "BFB2012BOT:Twitter:PerfilJA", discord.ButtonStyle.gray, os.getenv("emoji_ja"), None),
    botãocargo(881554833688125471, "BFB2012BOT:Twitter:PerfilFred", discord.ButtonStyle.gray, os.getenv("emoji_fred"), None),
    botãocargo(881555030933635142, "BFB2012BOT:Twitter:PerfilMarcus", discord.ButtonStyle.gray, os.getenv("emoji_marcus"), None)
)
botões_cores = (
    botãocargoexclusivo(773905344791052289, "BFB2012BOT:Cores:Esquizo", discord.ButtonStyle.red, "<:URSSLogo:809028237773897738>", "Esquizofrênico Comunista"),
    botãocargoexclusivo(789671247973056512, "BFB2012BOT:Cores:Caneta", discord.ButtonStyle.blurple, "\U0001f58a\ufe0f", "Caneta"),
    botãocargoexclusivo(740364615103414342, "BFB2012BOT:Cores:Furry",discord.ButtonStyle.blurple, "<:NekoConfused:809029527992139776>", "Furry")
)
botões_jogos = (
    botãocargo(836585359952969788, "BFB2012BOT:Jogos:Mine", discord.ButtonStyle.green, "<:Minecraft:932367213007093850>", "Minecraft"),
    botãocargo(932302842558021662, "BFB2012BOT:Jogos:Valas", discord.ButtonStyle.blurple, "<:Valorant:932368109602480169>", "Valorant"),
    botãocargo(742006890472669225, "BFB2012BOT:Jogos:LoL", discord.ButtonStyle.blurple, "<:LoL:932367529735761971>", "LoL")
)

class MeuBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conexao_motor = AsyncIOMotorClient(os.getenv("link_database"))
        self.database = self.conexao_motor.DiscordBot
        self.cache = {}
        self.conexão = aiohttp.ClientSession()
        self.emoji = {}
        self.cache_pronto = False
        self.flood = False
        self.viewadicionadas = False
    
    async def close(self):
        embed = discord.Embed(
            title = "Bot offline",
            description = f"Estou deslogando da conta {self.user} (ID: {self.user.id}) em {gethostname()}",
            color = 0xFF0000,
            timestamp = discord.utils.utcnow()
        )
        webhook = discord.Webhook.from_url(os.getenv("webhook_url"), session = self.conexão)
        await webhook.send(embed = embed)
        await self.conexão.close()
        self.conexao_motor.close()
        print("Conexões fechadas, desligando o bot...")
        await super().close()
    
    async def atualizar_cache(self, id):
        resultado = await self.database.servidores.find_one({"id_servidor": id})
        self.cache[id] = resultado

    async def on_ready(self):
        print("Estou logado no discord")
        emojis = bot.get_guild(801185265363845140).emojis
        for emoji in emojis:
            bot.emoji[emoji.name] = str(emoji)
        self.get_command("jsk").hidden = True
        self.cache[0] = await self.database.botinfos.find_one({})
        self.cache[1] = await self.database.twitter.find_one({})
        self.cache_pronto = True
        print("Estou pronto para receber comandos")
        embed = discord.Embed(
            title = "Bot online",
            description = f"Estou logado como {self.user} (ID: {self.user.id}) em {gethostname()}",
            color = 0x00FF00,
            timestamp = discord.utils.utcnow()
        )
        webhook = discord.Webhook.from_url(os.getenv("webhook_url"), session = self.conexão)
        await webhook.send(embed = embed)
        if not self.viewadicionadas:
            self.add_view(viewcargos(botões_rpg), message_id = 932385472288804864)
            self.add_view(viewcargos(botões_twitter), message_id = 932400568914292776)
            self.add_view(viewcargosexclusivos(botões_cores), message_id = 932412241389707284)
            self.add_view(viewcargos(botões_jogos), message_id = 932423919426748476)
            self.viewadicionadas = True

    async def on_message(self, mensagem):
        if mensagem.author.bot or not self.cache_pronto:
            return
        for prefixo in ("+", "b!", "B!"):
            if mensagem.content.startswith(prefixo):
                await self.process_commands(mensagem)
        for palavra in ('cringe', 'bluepill', 'redpill', 'based', 'chad'):
            if palavra in mensagem.content.lower().split():
                await mensagem.delete()
                return await mensagem.channel.send("https://media.discordapp.net/attachments/803443536363913236/873767769336852540/023590c9dcc5ced878f770522bde9245b032791291e7b410667ae33275df242e_1.jpg", delete_after = 20)
    
        for quanto in ('quantos ', 'quantas '):
            if quanto in mensagem.content.lower():
                quanto = quanto.replace(' ', '')
                lista_mensagem = mensagem.content.lower().split()
                palavra = lista_mensagem[lista_mensagem.index(quanto)+1]
                for ponto in ("?", ",", ".", "!"):
                    if ponto in palavra:
                        palavra = palavra.replace(ponto, '')
                await mensagem.channel.send(f"{random.randint(0, 101)} {palavra}")

    async def on_member_join(self, membro):
        if membro.guild.id == 719619736375394412:
            await membro.guild.get_channel(775319556682940416).send(f"<:PepeBoomer:802358097791287298> {membro.mention} você aqui de novo porra")

    async def on_member_remove(self, membro):
        if membro.guild.id == 719619736375394412:
            await membro.guild.get_channel(775319556682940416).send(f"<:PepeLaugh:802380913652531240> **{membro}** saiu pq é corno kkkkkk")

    async def on_command_error(self, ctx, error):
        texto = f"Esse erro não tem mensagem associada, com certeza é erro de código. Informações fodas: {error}"
        if isinstance(error, commands.MissingRequiredArgument):
            texto = "Você não escreveu tudo que precisava pro comando seu cabeça de pika"
        elif isinstance(error, commands.MemberNotFound):
            texto = "Você não passou um membro válido"
        elif isinstance(error, commands.BadArgument):
            texto = "Você passou alguma informação necessária pro comando de forma errada"
        elif isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.NotOwner):
            texto = "Esse comando é exclusivo para fodinhas (não vc)"
        elif isinstance(error, commands.MissingPermissions):
            texto = "Esse comando é exclusivo para fodinhas (não vckkkkk)"
        elif isinstance(error, Banido):
            texto = "Vc é um merdinha, fez alguma merda e agora você-sabe-quem te proibiu de usar comandos. Uma mamada e vc é desbanido (ctz q é o fred)"
        elif isinstance(error, commands.CommandOnCooldown):
            texto = f"Esse comando é limitado por tempo, tente novamente em {error.retry_after} segundos"
        elif isinstance(error, commands.MaxConcurrencyReached):
            texto = "Esse comando já está em execução o número máximo de vezes permitidas"
        elif isinstance(error, commands.NoPrivateMessage):
            texto = "Saaaaaai do meu pv seu abusador estuprador"
        await ctx.send(texto)

    async def on_raw_reaction_add(self, payload):
        if payload.guild_id:
            if payload.channel_id == 745288004041703516 and payload.message_id == 806950819894657104 and str(payload.emoji) == "<:BFB2012:804912558610972752>":
                servidor = bot.get_guild(payload.guild_id)
                cargo = servidor.get_role(719870617872105482)
                membro = servidor.get_member(payload.user_id)
                if cargo not in membro.roles:
                    await membro.add_roles(cargo)

    async def on_raw_reaction_remove(self, payload):
        if payload.guild_id:
            if payload.channel_id == 745288004041703516 and payload.message_id == 806950819894657104 and str(payload.emoji) == "<:BFB2012:804912558610972752>":
                servidor = bot.get_guild(payload.guild_id)
                cargo = servidor.get_role(719870617872105482)
                membro = servidor.get_member(payload.user_id)
                if cargo in membro.roles:
                    await membro.remove_roles(cargo)
    
class Banido(commands.CheckFailure):
    pass
    
intents = discord.Intents.all()
intents.invites = False
intents.voice_states = False
intents.typing = False

bot = MeuBot(
    command_prefix = ('+', "b!", "B!"),
    description = "BFB2012Bot",
    intents = intents,
    activity = discord.Activity(
        type = discord.ActivityType.listening,
        name = "Os gemidos da sua mãe"
    ),
    status = discord.Status.dnd#,
    #help_command = ajuda()
)

@bot.check
async def global_check(ctx):
    if not ctx.guild:
        raise commands.NoPrivateMessage
    if (ctx.author.id in ctx.bot.cache[0]["banidos"]):
        raise Banido
    return True

extensões = ("jishaku", "bfbcomandos", "bfbtwitter")
for extensão in extensões:
    bot.load_extension(extensão)

manter_ativo()
bot.ligou = discord.utils.utcnow()
bot.run(os.getenv("numeros_magicos"))
