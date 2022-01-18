import discord
from discord.ext import commands, tasks
from dateutil.parser import isoparse as dt_parse #upm package(python-dateutil)

import os
from urllib.parse import quote as percentage_encode
import base64
import random
from hashlib import sha1
import hmac
import time

class twitterview(discord.ui.View):
    def __init__(self, cog, id, link):
        super().__init__(timeout = 3600*12)
        self.cog =  cog
        self.id = id
        self.clear_items()
        self.add_item(self.curtir)
        self.add_item(self.retweet)
        self.add_item(discord.ui.Button(url = link, label = "Abrir no Twitter"))

    async def interaction_check(self, interação):
        if interação.user.guild_permissions.administrator:
            return True
        else:
            await interação.response.send_message("Você não pode realizar essa ação.", ephemeral = True)
            return False

    @discord.ui.button(label = "Curtir", emoji = "\u2764\ufe0f", style = discord.ButtonStyle.blurple)
    async def curtir(self, botão, interação):
        url_base = f"https://api.twitter.com/2/users/{self.cog.perfis[os.getenv('perfil_adm')]['id']}/likes"
        parametros_request = {
            "tweet_id": self.id
        }
        headers = self.cog.montar_oauth_twitter(url_base, "POST", {})
        async with self.cog.bot.conexão.post(url_base, headers = headers, json = parametros_request) as resposta:
            if resposta.status == 200:
                botão.disabled = True
                await interação.response.edit_message(view = self)
                await interação.followup.send("Tweet curtido com sucesso.", ephemeral = True)
            else:
                await interação.response.send_message(f"Deu ruim. Printa isso e me avisa.\nCódigo **{resposta.status}**\n\n{await resposta.json()}", ephemeral = True)

    @discord.ui.button(label = "Retweetar", emoji = "\U0001F501", style = discord.ButtonStyle.blurple)
    async def retweet(self, botão, interação):
        url_base = f"https://api.twitter.com/2/users/{self.cog.perfis[os.getenv('perfil_adm')]['id']}/retweets"
        parametros_request = {
            "tweet_id": self.id
        }
        headers = self.cog.montar_oauth_twitter(url_base, "POST", {})
        async with self.cog.bot.conexão.post(url_base, headers = headers, json = parametros_request) as resposta:
            if resposta.status == 200:
                botão.disabled = True
                await interação.response.edit_message(view = self)
                await interação.followup.send("Tweet retweetado com sucesso.", ephemeral = True)
            else:
                await interação.response.send_message(f"Deu ruim. Printa isso e me avisa.\nCódigo **{resposta.status}**\n\n{await resposta.json()}", ephemeral = True)

class twitter(
    commands.Cog,
    name = 'Twitter',
    description = 'Aqui você encontra coisas do twitter.'
):
    def __init__(self, bot):
        self.bot = bot
        self.autenticação_padrão = {'Authorization': f"Bearer {os.getenv('twitter_bearer')}"}
        self.perfis = {
            os.getenv("perfil_adm"): {
                "id": int(os.getenv("id_perfil_adm")),
                "cor": 0x1F59F2,
                "id_cargo": 812109324457345025},
            os.getenv("perfil_jp"): {
                "id": int(os.getenv("id_perfil_jp")),
                "cor": 0xE4B400,
                "id_cargo": 816835654763544596},
            os.getenv("perfil_ja"): {
                "id": int(os.getenv("id_perfil_ja")),
                "cor": 0x71368A,
                "id_cargo": 816835503382331463},
            os.getenv("perfil_fred"): {
                "id": int(os.getenv("id_perfil_fred")),
                "cor": 0x6D767C,
                "id_cargo": 881554833688125471},
            os.getenv("perfil_marcus"): {
                "id": int(os.getenv("id_perfil_marcus")),
                "cor": 0xEA1B0D,
                "id_cargo": 881555030933635142}
        }
        self.url_pesquisa_posts = f"https://api.twitter.com/2/tweets/search/recent?max_results=10"\
        f"&query=from:" + "%20OR%20from:".join([perfil for perfil in self.perfis]) #"{self.perfil_1}%20OR%20from:{self.perfil_2}%20OR%20from:{self.perfil_3}%20OR%20from:{self.perfil_4}%20OR%20from:{self.perfil_5}"\
        self.url_pesquisa_posts += "&expansions=attachments.poll_ids,attachments.media_keys,referenced_tweets.id.author_id,author_id"\
        "&media.fields=media_key,preview_image_url,type,url"\
        "&poll.fields=duration_minutes,end_datetime,id,options,voting_status"\
        "&tweet.fields=attachments,created_at,entities,id,lang,public_metrics,possibly_sensitive,referenced_tweets,source,text,withheld"\
        "&user.fields=name,profile_image_url"
        self.consumer_key = os.getenv("twitter_consumer_key")
        self.consumer_secret = os.getenv("twitter_consumer_secret")
        self.acess_token = os.getenv("twitter_acess_token")
        self.acess_secret = os.getenv("twitter_acess_secret")
        self.verificar_posts.start()

    def cog_unload(self):
        self.verificar_posts.cancel()

    def montar_oauth_twitter(self, url_base, metodo, parametros_request):
        parametros_autenticação = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_nonce": base64.b64encode(bytearray([random.randint(0,255) for i in range(32)])).decode("ascii"),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(time.time()),
            "oauth_token": self.acess_token,
            "oauth_version": "1.0"
        }
        parametros_gerais = {**parametros_request, **parametros_autenticação}
        for chave in parametros_gerais:
            parametros_gerais[chave] = percentage_encode(parametros_gerais[chave], safe = "")
        parametros_gerais = dict(sorted(parametros_gerais.items()))
        parameter_string = ""
        for chave in parametros_gerais:
            parameter_string += chave + "=" + parametros_gerais[chave] + "&"
        parameter_string = parameter_string[:-1]
        assinatura = metodo + "&" + percentage_encode(url_base, safe = "") + "&" + percentage_encode(parameter_string, safe = "")
        assinatura = bytearray(assinatura.encode())
        signing_key = percentage_encode(self.consumer_secret, safe = "") + "&" + percentage_encode(self.acess_secret, safe = "")
        signing_key = bytearray(signing_key.encode())
        parametros_autenticação["oauth_signature"] = base64.urlsafe_b64encode(hmac.new(signing_key, assinatura, sha1).digest())
        DST = "OAuth "
        for chave in parametros_autenticação:
            DST += percentage_encode(chave, safe = "") + "=\"" + percentage_encode(parametros_autenticação[chave], safe = "") + "\", "
        DST = DST[:-2]
        return {"Authorization": DST}

    def retornar_embed_twitter(self, post, anexos):
        autor = "Não foi possivel conseguir o nome do autor"
        for usuario in anexos['users']:
            if usuario['id'] == post['author_id']:
                autor = usuario['name']
        embed = discord.Embed(
            title = f"Exibindo tweet de **@{autor}**",
            description = "\"" + post['text'] + "\"",
            color = 0x57c7FF,
            timestamp = dt_parse(post['created_at'])
        ).add_field(
            name = "Informações do Tweet",
            value = f"Postado de \"{post['source']}\"\nID: {post['id']}\n\u2764\ufe0f {post['public_metrics']['like_count']} | \U0001f4ac {post['public_metrics']['reply_count']} | \U0001f5ef\ufe0f {post['public_metrics']['quote_count']} | \U0001f501 {post['public_metrics']['retweet_count']}",
            inline = False
        ).set_footer(
            text = "twitter.com | Tweet feito em",
            icon_url = "https://media.discordapp.net/attachments/803443536363913236/874767316108341258/580b57fcd9996e24bc43c53e.png"
        )
        if 'referenced_tweets' in post:
            for tweet_referenciado in post['referenced_tweets']:
                if tweet_referenciado['type'] == 'replied_to':
                    id_tweet = tweet_referenciado['id']
                    for tweet in anexos['tweets']:
                        if tweet['id'] == id_tweet:
                            nome_autor_referenciado = "(Não foi possível obter o nome do autor)"
                            for usuario in anexos['users']:
                                if usuario['id'] == tweet['author_id']:
                                    nome_autor_referenciado = usuario['name']
                                    break
                            embed.add_field(
                                name = "Resposta",
                                value = f"Esse tweet responde a um tweet postado originalmente por {nome_autor_referenciado}.\n**Conteúdo**: \"{tweet['text']}\""
                            )
                            break
        if 'attachments' in post:
            if 'media_keys' in post['attachments']:
                id_midia = post['attachments']['media_keys'][0]
                for midia in anexos['media']:
                    if midia['media_key'] == id_midia:
                        if midia['type'] == 'photo':
                            embed.set_image(
                                url = midia['url']
                            ).add_field(
                                name = "Anexos",
                                value =  f"Tipo de mídia anexada: Imagem\nNúmero de mídias: {len(post['attachments']['media_keys'])}",
                                inline = False
                            )
                            break
                        elif midia['type'] == 'video':
                            embed.set_image(
                                url = midia['preview_image_url']
                            ).add_field(
                                name = "Anexos",
                                value = "Tipo de mídia anexada: Vídeo (exibindo thumbnail)",
                                inline = False
                            )
                            break
                        elif midia['type'] == 'animated_gif':
                            embed.set_image(
                                url = midia['preview_image_url']
                            ).add_field(
                                name = "Anexos",
                                value = "Tipo de mídia anexada: Gif (Exibindo thumbnail)",
                                inline = False
                            )
                            break
            elif 'poll_ids' in post['attachments']:
                id_enquete = post['attachments']['poll_ids'][0]
                for enquete in anexos['polls']:
                    if enquete['id'] == id_enquete:
                        enquete['options'].sort(key = lambda e: str(e['position']))
                        embed.add_field(
                            name = "Enquete",
                            value = f"Termina em: {enquete['end_datetime'].replace('-', '/').replace('T', '  ')}",
                            inline = False
                        ).add_field(
                            name = "Opções",
                            value = "\n".join([infos['label'] for infos in enquete['options']]),
                            inline = True
                        ).add_field(
                            name = "Votos",
                            value = "\n".join([str(infos['votes']) for infos in enquete['options']]),
                            inline = True
                        )
                        break
        return embed
    
    @commands.group(aliases = ("t",), invoke_without_command = True)
    async def twitter(self, ctx):
        """Comandos relacionados ao twitter"""
        await ctx.send_help("twitter")

    @twitter.command()
    @commands.has_permissions(administrator = True)
    @commands.cooldown(1, 1800, commands.BucketType.user)
    async def postar(self, ctx, *,texto):
        """Posta um tweet na conta de titter do bfb."""
        url_base = f"https://api.twitter.com/1.1/statuses/update.json"
        parametros_request = {
            "status": texto
        }
        headers = self.montar_oauth_twitter(url_base, "POST", parametros_request)
        async with self.bot.conexão.post(url_base, headers = headers, data = parametros_request) as resposta:
            if resposta.status == 200:
                await ctx.send("O tweet foi postado com sucesso. Verifique o canal de avisos do Twitter.")
            else:
                await ctx.send(f"Houve um problema ao postar o tweet. As informações do erro são:\nCódigo **{resposta.status}**\n\n{await resposta.json()}")

    @twitter.command()
    @commands.has_permissions(administrator = True)
    @commands.cooldown(3, 1800, commands.BucketType.user)
    async def responder(self, ctx, id: int, *, texto):
        """Responde um tweet. Você precisa informar o id do tweet (é possivel ver ele no comando de posts) e precisa marcar o autor dele para que a resposta seja contabilizada."""
        url_base = f"https://api.twitter.com/1.1/statuses/update.json"
        parametros_request = {
            "status": texto,
            "in_reply_to_status_id": str(id)
        }
        headers = self.montar_oauth_twitter(url_base, "POST", parametros_request)
        async with self.bot.conexão.post(url_base, headers = headers, data = parametros_request) as resposta:
            if resposta.status == 200:
                await ctx.send("O tweet foi postado com sucesso. Verifique o canal de avisos do Twitter.")
            else:
                await ctx.send(f"Houve um problema ao postar o tweet. As informaçṍes do erro são:\nCódigo **{resposta.status}**\n\n{await resposta.json()}")

    @tasks.loop(seconds = 15)
    async def verificar_posts(self):
        if not self.bot.cache_pronto:
            return
        canal_avisos = self.bot.get_guild(719619736375394412).get_channel(801235678536269865)
        ultimo_tweet_id = self.bot.cache[1]['ultimo_tweet_id']
        url = self.url_pesquisa_posts + f"&since_id={ultimo_tweet_id}"
        async with self.bot.conexão.get(url, headers = self.autenticação_padrão) as resposta:
            json = await resposta.json()
            if json['meta']['result_count'] > 0:
                for post in json["data"]:
                    for autor in self.perfis:
                        if int(post['author_id']) == self.perfis[autor]["id"] and int(post["id"]) > self.bot.cache[1]["tweet_id"][autor]:
                            embed = self.retornar_embed_twitter(post, json["includes"])
                            embed.title = f"Post novo feito por **@{autor}**"
                            embed.color = self.perfis[autor]["cor"]
                            link_post = f"https://twitter.com/{autor}/status/{post['id']}"
                            await canal_avisos.send(f"<@&{self.perfis[autor]['id_cargo']}>", embed = embed, view = twitterview(self, post["id"], link_post))
                            await self.bot.database.twitter.update_one(
                                {},
                                {"$set": {f"tweet_id.{autor}": int(post['id'])}}
                            )
                            break
                await self.bot.database.twitter.update_one(
                    {},
                    {"$set": {"ultimo_tweet_id": int(json['data'][0]['id'])}}
                )
                self.bot.cache[1] = await self.bot.database.twitter.find_one({})
    
    @verificar_posts.before_loop
    async def antes(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(twitter(bot))
 
