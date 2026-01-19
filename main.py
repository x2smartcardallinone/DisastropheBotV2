import discord
import os
import json
from discord.ext import commands
from discord import app_commands, ui

# Load settings to get prefix
try:
    with open('Settings.json', 'r') as f:
        settings = json.load(f)
        prefix = settings.get('Prefix', '!')
except Exception:
    prefix = '!'

TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

# Config por servidor (Status Role)
try:
    with open('setups.json', 'r') as f:
        SETUPS = json.load(f)
        SETUPS = {int(k): v for k, v in SETUPS.items()}
except:
    SETUPS = {}

def save_setups():
    with open('setups.json', 'w') as f:
        json.dump(SETUPS, f)

# Member Count Embed Config (Mimu style)
try:
    with open('counter_config.json', 'r') as f:
        config = json.load(f)
        EMBED_DATA = config.get('embed_data', {
            "title": "welcome to the server",
            "description": "👥 Members: {member_count}",
            "color": 0x5865F2,
            "author": {"name": None, "icon": None},
            "footer": {"text": None, "icon": None},
            "image": None,
            "thumbnail": None
        })
        COUNTER_MESSAGE_ID = config.get('msg_id')
        COUNTER_CHANNEL_ID = config.get('channel_id', 1454266749426995273)
except:
    EMBED_DATA = {
        "title": "welcome to the server",
        "description": "👥 Members: {member_count}",
        "color": 0x5865F2,
        "author": {"name": None, "icon": None},
        "footer": {"text": None, "icon": None},
        "image": None,
        "thumbnail": None
    }
    COUNTER_MESSAGE_ID = None
    COUNTER_CHANNEL_ID = 1454266749426995273

EMBED_MESSAGE = None

def save_counter_config():
    with open('counter_config.json', 'w') as f:
        json.dump({
            'embed_data': EMBED_DATA,
            'msg_id': COUNTER_MESSAGE_ID,
            'channel_id': COUNTER_CHANNEL_ID
        }, f)

def render_embed(guild):
    # Count humans (non-bots)
    humans = len([m for m in guild.members if not m.bot])
    data = {
        "member_count": guild.member_count,
        "human_count": humans
    }
    
    title = EMBED_DATA["title"].format(**data) if EMBED_DATA["title"] else None
    desc = EMBED_DATA["description"].format(**data) if EMBED_DATA["description"] else None
    
    e = discord.Embed(
        title=title,
        description=desc,
        color=EMBED_DATA["color"]
    )
    
    if EMBED_DATA["author"]["name"]:
        e.set_author(
            name=EMBED_DATA["author"]["name"].format(**data),
            icon_url=EMBED_DATA["author"]["icon"]
        )
        
    if EMBED_DATA["footer"]["text"]:
        e.set_footer(
            text=EMBED_DATA["footer"]["text"].format(**data),
            icon_url=EMBED_DATA["footer"]["icon"]
        )
        
    if EMBED_DATA["image"]:
        e.set_image(url=EMBED_DATA["image"])
        
    if EMBED_DATA["thumbnail"]:
        e.set_thumbnail(url=EMBED_DATA["thumbnail"])
        
    return e

async def update_embed(guild):
    global COUNTER_MESSAGE_ID, EMBED_MESSAGE
    
    # Update the permanent counter message if it exists
    if COUNTER_MESSAGE_ID:
        channel = bot.get_channel(COUNTER_CHANNEL_ID)
        if channel:
            try:
                msg = await channel.fetch_message(COUNTER_MESSAGE_ID)
                await msg.edit(embed=render_embed(guild))
            except:
                pass

    # Update the temporary editor preview message if it exists
    if EMBED_MESSAGE:
        try:
            await EMBED_MESSAGE.edit(
                embed=render_embed(guild),
                view=EmbedEditorView()
            )
        except:
            EMBED_MESSAGE = None

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot activo"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- Modals ---

class BasicModal(ui.Modal, title="Edit Basic Information"):
    title_input = ui.TextInput(label="Title", required=False, default=EMBED_DATA["title"])
    desc_input = ui.TextInput(label="Description", style=discord.TextStyle.paragraph, required=False, default=EMBED_DATA["description"])
    color_input = ui.TextInput(label="Hex Color (#5865F2)", required=False, default=f"#{hex(EMBED_DATA['color'])[2:].zfill(6)}")

    async def on_submit(self, interaction):
        EMBED_DATA["title"] = self.title_input.value or None
        if self.desc_input.value: EMBED_DATA["description"] = self.desc_input.value
        if self.color_input.value:
            try: EMBED_DATA["color"] = int(self.color_input.value.replace("#", ""), 16)
            except: pass
        save_counter_config()
        await update_embed(interaction.guild)
        await interaction.response.send_message("✅ Updated Basic", ephemeral=True)

class AuthorModal(ui.Modal, title="Edit Author"):
    name = ui.TextInput(label="Author Name", required=False, default=EMBED_DATA["author"]["name"] or "")
    icon = ui.TextInput(label="Author Icon URL", required=False, default=EMBED_DATA["author"]["icon"] or "")

    async def on_submit(self, interaction):
        EMBED_DATA["author"]["name"] = self.name.value or None
        EMBED_DATA["author"]["icon"] = self.icon.value or None
        save_counter_config()
        await update_embed(interaction.guild)
        await interaction.response.send_message("✅ Updated Author", ephemeral=True)

class FooterModal(ui.Modal, title="Edit Footer"):
    text = ui.TextInput(label="Footer Text", required=False, default=EMBED_DATA["footer"]["text"] or "")
    icon = ui.TextInput(label="Footer Icon URL", required=False, default=EMBED_DATA["footer"]["icon"] or "")

    async def on_submit(self, interaction):
        EMBED_DATA["footer"]["text"] = self.text.value or None
        EMBED_DATA["footer"]["icon"] = self.icon.value or None
        save_counter_config()
        await update_embed(interaction.guild)
        await interaction.response.send_message("✅ Updated Footer", ephemeral=True)

class ImagesModal(ui.Modal, title="Edit Images"):
    image = ui.TextInput(label="Image URL", required=False, default=EMBED_DATA["image"] or "")
    thumb = ui.TextInput(label="Thumbnail URL", required=False, default=EMBED_DATA["thumbnail"] or "")

    async def on_submit(self, interaction):
        EMBED_DATA["image"] = self.image.value or None
        EMBED_DATA["thumbnail"] = self.thumb.value or None
        save_counter_config()
        await update_embed(interaction.guild)
        await interaction.response.send_message("✅ Updated Images", ephemeral=True)

class EmbedEditorView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="edit basic", style=discord.ButtonStyle.secondary)
    async def basic(self, interaction, button):
        await interaction.response.send_modal(BasicModal())

    @ui.button(label="edit author", style=discord.ButtonStyle.secondary)
    async def author(self, interaction, button):
        await interaction.response.send_modal(AuthorModal())

    @ui.button(label="edit footer", style=discord.ButtonStyle.secondary)
    async def footer(self, interaction, button):
        await interaction.response.send_modal(FooterModal())

    @ui.button(label="edit images", style=discord.ButtonStyle.secondary)
    async def images(self, interaction, button):
        await interaction.response.send_modal(ImagesModal())

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Conectado como {bot.user}")

@bot.tree.command(name="embed_edit", description="Edit embed dashboard (Mimu style)")
@app_commands.checks.has_permissions(administrator=True)
async def embed_edit(interaction: discord.Interaction):
    global EMBED_MESSAGE
    await interaction.response.send_message(
        embed=render_embed(interaction.guild),
        view=EmbedEditorView(),
        ephemeral=True
    )
    EMBED_MESSAGE = await interaction.original_response()

@bot.tree.command(name="setup_counter", description="Setup member counter embed")
@app_commands.checks.has_permissions(administrator=True)
async def setup_counter(interaction: discord.Interaction):
    global COUNTER_MESSAGE_ID
    # Removed defer to prevent "Unknown interaction" error if Render/Discord delay happens
    channel = bot.get_channel(COUNTER_CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("❌ No se encontró el canal de contador.", ephemeral=True)
        return
    
    try:
        msg = await channel.send(embed=render_embed(interaction.guild))
        COUNTER_MESSAGE_ID = msg.id
        save_counter_config()
        await interaction.response.send_message(f"✅ Contador configurado en {channel.mention}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error al enviar el mensaje: {e}", ephemeral=True)

@bot.event
async def on_member_join(member):
    await update_embed(member.guild)

@bot.event
async def on_member_remove(member):
    await update_embed(member.guild)

# --- Status Role ---
@bot.tree.command(name="setup", description="Setup vanity role")
@app_commands.describe(custom_status="Texto exacto del status (ej: /disastrophe)", role="Rol a asignar")
async def setup(interaction: discord.Interaction, custom_status: str, role: discord.Role):
    await interaction.response.defer(ephemeral=True)
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.followup.send("❌ No tienes permisos", ephemeral=True)
        return
    SETUPS[interaction.guild.id] = {"text": custom_status, "role_id": role.id}
    save_setups()
    await interaction.followup.send(f"✅ Setup completo\nStatus: `{custom_status}`\nRol: {role.mention}", ephemeral=True)

@bot.event
async def on_presence_update(before, after):
    guild = after.guild
    if not guild or guild.id not in SETUPS: return
    data = SETUPS[guild.id]
    role = guild.get_role(data["role_id"])
    if not role: return
    has_match = any(a.type == discord.ActivityType.custom and a.name and data["text"] in a.name for a in after.activities)
    try:
        if has_match and role not in after.roles: await after.add_roles(role)
        elif not has_match and role in after.roles: await after.remove_roles(role)
    except: pass

if TOKEN: 
    keep_alive()
    bot.run(TOKEN)
else: print("Error: DISCORD_BOT_TOKEN not found.")
