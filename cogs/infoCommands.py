import discord from discord.ext import commands from discord import app_commands import aiohttp from datetime import datetime import json import os import asyncio import io import uuid import gc from datetime import datetime

CONFIG_FILE = "info_channels.json"

class InfoCommands(commands.Cog): def init(self, bot): self.bot = bot self.api_url = "https://glob-info.vercel.app/info" self.generate_url = "https://genprofile.vercel.app/generate" self.session = aiohttp.ClientSession() self.config_data = self.load_config() self.cooldowns = {}

def convert_unix_timestamp(self ,timestamp: int) -> str:
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def check_request_limit(self, guild_id):
    try:
        return self.is_server_subscribed(guild_id) or not self.is_limit_reached(guild_id)
    except Exception as e:
        print(f"Error checking request limit: {e}")
        return False

def load_config(self):
    default_config = {
        "servers": {},
        "global_settings": {
            "default_all_channels": False,
            "default_cooldown": 30,
            "default_daily_limit": 30
        }
    }

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                loaded_config = json.load(f)
                loaded_config.setdefault("global_settings", {})
                loaded_config["global_settings"].setdefault("default_all_channels", False)
                loaded_config["global_settings"].setdefault("default_cooldown", 30)
                loaded_config["global_settings"].setdefault("default_daily_limit", 30)
                loaded_config.setdefault("servers", {})
                return loaded_config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            return default_config
    return default_config

def save_config(self):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config_data, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving config: {e}")

async def is_channel_allowed(self, ctx):
    try:
        guild_id = str(ctx.guild.id)
        allowed_channels = self.config_data["servers"].get(guild_id, {}).get("info_channels", [])

        if not allowed_channels:
            return True

        return str(ctx.channel.id) in allowed_channels
    except Exception as e:
        print(f"Error checking channel permission: {e}")
        return False

@commands.hybrid_command(name="setinfochannel", description="Allow a channel for !info commands")
@commands.has_permissions(administrator=True)
async def set_info_channel(self, ctx: commands.Context, channel: discord.TextChannel):
    guild_id = str(ctx.guild.id)
    self.config_data["servers"].setdefault(guild_id, {"info_channels": [], "config": {}})
    if str(channel.id) not in self.config_data["servers"][guild_id]["info_channels"]:
        self.config_data["servers"][guild_id]["info_channels"].append(str(channel.id))
        self.save_config()
        await ctx.send(f"✅ {channel.mention} está agora permitido para comandos `!info`")
    else:
        await ctx.send(f"ℹ️ {channel.mention} já está permitido para comandos `!info`")

@commands.hybrid_command(name="removeinfochannel", description="Remove a channel from !info commands")
@commands.has_permissions(administrator=True)
async def remove_info_channel(self, ctx: commands.Context, channel: discord.TextChannel):
    guild_id = str(ctx.guild.id)
    if guild_id in self.config_data["servers"]:
        if str(channel.id) in self.config_data["servers"][guild_id]["info_channels"]:
            self.config_data["servers"][guild_id]["info_channels"].remove(str(channel.id))
            self.save_config()
            await ctx.send(f"✅ {channel.mention} foi removido dos canais permitidos")
        else:
            await ctx.send(f"❌ {channel.mention} não está na lista de canais permitidos")
    else:
        await ctx.send("ℹ️ Este servidor não possui configurações salvas")

@commands.hybrid_command(name="infochannels", description="List allowed channels")
async def list_info_channels(self, ctx: commands.Context):
    guild_id = str(ctx.guild.id)

    if guild_id in self.config_data["servers"] and self.config_data["servers"][guild_id]["info_channels"]:
        channels = []
        for channel_id in self.config_data["servers"][guild_id]["info_channels"]:
            channel = ctx.guild.get_channel(int(channel_id))
            channels.append(f"• {channel.mention if channel else f'ID: {channel_id}'}")

        embed = discord.Embed(
            title="Canais permitidos para !info",
            description="\n".join(channels),
            color=discord.Color.blue()
        )
        cooldown = self.config_data["servers"][guild_id]["config"].get("cooldown", self.config_data["global_settings"]["default_cooldown"])
        embed.set_footer(text=f"Cooldown atual: {cooldown} segundos")
    else:
        embed = discord.Embed(
            title="Canais permitidos para !info",
            description="Todos os canais estão permitidos (nenhuma restrição configurada)",
            color=discord.Color.blue()
        )

    await ctx.send(embed=embed)

# O restante do comando info será inserido na próxima atualização (continuando o código)

async def cog_unload(self):
    await self.session.close()

async def _send_player_not_found(self, ctx, uid):
    embed = discord.Embed(
        title="❌ Jogador Não Encontrado",
        description=(
            f"UID `{uid}` não encontrado ou inacessível.\n\n"
            "⚠️ **Nota:** Servidores IND estão atualmente fora do ar."
        ),
        color=0xE74C3C
    )
    embed.add_field(
        name="Dica",
        value="- Certifique-se de que o UID está correto\n- Tente outro UID",
        inline=False
    )
    await ctx.send(embed=embed, ephemeral=True)

async def _send_api_error(self, ctx):
    await ctx.send(embed=discord.Embed(
        title="⚠️ Erro na API",
        description="A API do Free Fire não está respondendo. Tente novamente mais tarde.",
        color=0xF39C12
    ))

async def setup(bot): await bot.add_cog(InfoCommands(bot))

