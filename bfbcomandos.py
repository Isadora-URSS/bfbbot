import discord
from discord.ext import commands, tasks

import os
import asyncio
import time
import random

class comandos(
    commands.Cog,
    name = "comandos",
    description = "Essa categoria contem comandos"
):
    def __init__(self, bot):
        self.bot = bot
        self.rickrolls = (
            "https://youtu.be/DLzxrzFCyOs",
            "https://youtu.be/CFVPW6oV67s",
            "https://youtu.be/34Ig3X59_qA",
            "https://youtu.be/pvJnMhvYscE",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://youtu.be/X_8Nh5XfRw0",
            "https://youtu.be/u6NOTogsw8M",
            "https://youtu.be/59O0TgS7EMI",
            "https://youtu.be/0nfLPq7-K2w",
            "https://open.spotify.com/track/6VPOVkex1tTqsMlMyH8Ebf?si=JEYWITQdS5CIrpoPdonHcA&utm_source=copy-link",
            "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT?si=nt4kQDqvS4OakLsKMEYB7w&utm_source=copy-link"
        )
        self.evento = asyncio.Event()
        self.preparararmas_rodando = False
        #self.rickroll.start()

    async def esperar_cessarfogo(self):
        await self.evento.wait()
    
    @tasks.loop(minutes = 10)
    async def rickroll(self):
        if random.randint(0, 50) == 1:
            canal = random.choice(self.bot.get_guild(719619736375394412).text_channels)
            rickroll = random.choice(self.rickrolls)
            await canal.send(f"<{rickroll}>")
        else:
            return

    @commands.command()
    async def tetadojp(self, ctx):
        """Manda a teta do jp"""
        await ctx.send(embed = discord.Embed(
            title = "Parece até de menina hmm",
            color = 0xd9b0b0
        ).set_image(
            url = os.getenv("teta_do_jp")
        ))
    
    @commands.command()
    async def pedojp(self, ctx):
        """Manda o pezinho do jp"""
        await ctx.send(embed = discord.Embed(
            title = "Fiquei de pé duro",
            color = 0xd9b0b0
        ).set_image(
            url = os.getenv("pe_do_jp")
        ))
    
    @commands.command()
    async def tetadomarcus(self, ctx):
        """Manda a teta do marcus"""
        await ctx.send(embed = discord.Embed(
            title = "Tankinho",
            color = 0xd9b0b0
        ).set_image(
            url = os.getenv("teta_do_marcus")
        ))
    
    @commands.command()
    async def sucrilhos(self, ctx):
        """Zoa o j.a pq ele não tem sucrilhos"""
        await ctx.send(embed = discord.Embed(
            title = "JÃO ARTHUR NÃO TEM SUCRILHOS KKKKKKK",
            color = 0x70FF70
        ).set_image(
            url = "https://media.discordapp.net/attachments/299263252808990721/719958187381620736/520cadb1-8b78-4a81-8337-c8ca192104da.png"
        ))

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def flood(self, ctx, quantia: int, *,frase):
        """Faz spam de uma mensagem"""
        if quantia <= 0:
            await ctx.send("Dá um número que preste fdp")
        else:
            webhook = await ctx.channel.create_webhook(name = "Flood")
            nome = str(ctx.author).split("#")[0]
            for i in range(quantia):
                if self.bot.flood != True:
                    await webhook.send(frase, username = nome, avatar_url = ctx.author.avatar.url)
                    await asyncio.sleep(0.9)
                else:
                    await webhook.delete()
                    await ctx.send(f"TABÃO TABÃO EU NÃO VOU AGUENTA MAIS TIRA TIRA TIRA CARAIO ({i})")
                    self.bot.flood = False
                    return
            await webhook.delete()
            await ctx.send(f"Terminei de manda oq vc pediu ({quantia})")
    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def paraflood(self, ctx):
        """Para o flood"""
        self.bot.flood = True
        await ctx.message.add_reaction("\u2714\ufe0f")
    
    @commands.command()
    async def ping(self, ctx):
        """Envia a latência do bot"""
        começo = time.perf_counter()
        mensagem = await ctx.send("Calculando...")
        fim = time.perf_counter()
        duração = round((fim - começo)*1000, 2)
        começo2 = time.perf_counter()
        await self.bot.conexao_motor.admin.command({"ping": 1})
        fim2 = time.perf_counter()
        duração_database = round((fim2 - começo2)*1000,2)
        duração_websocket = round(self.bot.latency*1000, 2)
        await mensagem.edit(
            content = f"{ctx.author.mention}, calculei!\nTempo para envio de mensagem: {duração}ms.\nLatência do websocket: {duração_websocket}ms.\nLatência da database: {duração_database}ms."
        )
    
    @commands.command()
    async def uptime(self, ctx):
        """Manda o tempo de atividade do bot"""
        await ctx.send(f"O bot está ativo desde <t:{int(self.bot.ligou.timestamp())}> (<t:{int(self.bot.ligou.timestamp())}:R>)")
    
    @commands.command()
    @commands.is_owner()
    async def atualizarcache(self, ctx):
        """Atualiza o cache do bot"""
        self.bot.cache[0] = await self.bot.database.botinfos.find_one({})
        self.bot.cache[1] = await self.bot.database.twitter.find_one({})
        await ctx.message.add_reaction("\u2714\ufe0f")

    @commands.command(aliases = ("prepararmas", "apontarfogo", "apontararma", "prepararfogo"))
    @commands.has_permissions(ban_members = True)
    @commands.max_concurrency(1, commands.BucketType.default)
    async def preparararmas(self, ctx, membro: discord.Member, tempo: int):
        """Incia um contador para banir alguem. Se o comando cessarfogo não for usado nesse periodo, o alvo será banido. Se ele for usado, o alvo não será banido. O tempo passado é em segundos"""
        if membro.guild_permissions.administrator or ctx.guild.roles.index(membro.top_role) >= ctx.guild.roles.index(ctx.author.top_role):
            return await ctx.send("Você não tem poder para usar o comando nesse membro")
        self.preparararmas_rodando = True
        await ctx.send(f"{membro.mention}, você tem {tempo} segundos para responder.")
        try:
            await asyncio.wait_for(self.esperar_cessarfogo(), timeout = tempo)
        except asyncio.TimeoutError:
            await ctx.guild.ban(membro, delete_message_days = 0)
            await ctx.send("Bani o alvo do comando.")
        else:
            self.evento.clear()
            await ctx.send("Fogo cancelado.")
        self.preparararmas_rodando = False
        
    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def cessarfogo(self, ctx):
        """Interrompe um comando preparararmas em andamento"""
        if not self.preparararmas_rodando:
            await ctx.send("As armas não estão apontadas")
        else:
            self.evento.set()
    
def setup(bot):
    bot.add_cog(comandos(bot))
