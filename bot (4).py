import discord
from discord.ext import commands
from discord import app_commands
import os
from config import CONFIG

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=CONFIG["prefix"], intents=intents, help_command=None)


# ══════════════════════════════════════════════
#  TICKET — Bouton fermer
# ══════════════════════════════════════════════
class BoutonFermerTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Fermer le ticket", style=discord.ButtonStyle.red, custom_id="fermer_ticket")
    async def fermer(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description=f"Ticket fermé par {interaction.user.mention}. Suppression dans **5 secondes**.",
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed)
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()


# ══════════════════════════════════════════════
#  TICKET — Bouton ouvrir (sur l'embed produit)
# ══════════════════════════════════════════════
class BoutonTicket(discord.ui.View):
    def __init__(self, type_ticket: str, label_btn: str, resume: str):
        super().__init__(timeout=None)
        self.type_ticket = type_ticket
        self.resume      = resume
        btn = discord.ui.Button(label=label_btn, style=discord.ButtonStyle.green, custom_id=f"open_{type_ticket}", emoji="🎫")
        btn.callback = self.ouvrir
        self.add_item(btn)

    async def ouvrir(self, interaction: discord.Interaction):
        guild  = interaction.guild
        member = interaction.user

        # Catégorie
        cat_name = CONFIG.get("ticket_category", "📩 TICKETS")
        categorie = discord.utils.get(guild.categories, name=cat_name) or await guild.create_category(cat_name)

        nom_salon = f"ticket-{member.name}".lower().replace(" ", "-")[:100]

        # Vérif ticket existant
        if discord.utils.get(guild.text_channels, name=nom_salon):
            await interaction.response.send_message("❌ Tu as déjà un ticket ouvert !", ephemeral=True)
            return

        staff_role = guild.get_role(CONFIG["staff_role_id"]) if CONFIG.get("staff_role_id") else None
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member:             discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me:           discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
        }
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        salon = await guild.create_text_channel(name=nom_salon, category=categorie, overwrites=overwrites)

        embed = discord.Embed(color=discord.Color.from_str(CONFIG["embed_color"]))
        embed.add_field(name=f"👋 Bienvenue {member.display_name} !", value="\u200b", inline=False)
        embed.add_field(name="\u200b", value="Merci d'avoir ouvert un ticket.\nUn membre du staff va te répondre rapidement.", inline=False)
        embed.add_field(name="\u200b", value=f"**Commande :** {self.resume}", inline=False)
        embed.add_field(name="\u200b", value=f"⏰ Temps de réponse : {CONFIG.get('response_time', '< 24h')}", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=CONFIG.get("owner_name", "Support"), icon_url=bot.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        mention = f"<@&{CONFIG['staff_role_id']}>" if CONFIG.get("staff_role_id") else ""
        await salon.send(content=f"{mention} {member.mention}", embed=embed, view=BoutonFermerTicket())
        await interaction.response.send_message(f"✅ Ticket créé : {salon.mention}", ephemeral=True)


# ══════════════════════════════════════════════
#  MODAL — /compte  (popup libre)
# ══════════════════════════════════════════════
class CompteModal(discord.ui.Modal, title="🧾 Nouvelle fiche compte"):

    champ_titre = discord.ui.TextInput(
        label="Titre",
        placeholder="Ex: New Account | 1775243294683",
        required=True,
        max_length=256,
    )
    champ_description = discord.ui.TextInput(
        label="Description",
        placeholder="Écris librement, tu peux faire des retours à la ligne, mettre des emojis...",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=1024,
    )
    champ_stats = discord.ui.TextInput(
        label="Stats / Infos",
        placeholder="💰 Price — 550€\n🏆 Trophies — 95000\n...",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=1024,
    )
    champ_image = discord.ui.TextInput(
        label="URL de l'image (optionnel)",
        placeholder="https://...",
        required=False,
    )
    champ_btn = discord.ui.TextInput(
        label="Texte du bouton de commande",
        placeholder="Ex: 🧾 Commander  /  💳 Acheter",
        required=True,
        max_length=80,
        default="🧾 Commander",
    )

    def __init__(self, salon, couleur):
        super().__init__()
        self.salon   = salon
        self.couleur = couleur

    async def on_submit(self, interaction: discord.Interaction):
        try:
            color = discord.Color.from_str(self.couleur) if self.couleur else discord.Color.from_str(CONFIG["embed_color"])
        except Exception:
            color = discord.Color.from_str(CONFIG["embed_color"])

        # Titre = embed.title (gros gras auto par Discord)
        # Description = embed.description (texte normal)
        # Ligne fine apparait automatiquement entre description et field
        desc = self.champ_description.value.strip() or None
        embed = discord.Embed(
            title       = self.champ_titre.value,
            description = desc,
            color       = color,
        )
        if self.champ_stats.value.strip():
            embed.add_field(name="\u200b", value=self.champ_stats.value, inline=False)
        if self.champ_image.value.strip():
            embed.set_image(url=self.champ_image.value.strip())
        embed.set_footer(text=CONFIG.get("owner_name", "Boutique"), icon_url=bot.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        view   = BoutonTicket(type_ticket="compte", label_btn=self.champ_btn.value, resume=self.champ_titre.value)
        target = self.salon or interaction.channel
        await target.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Fiche envoyée !", ephemeral=True)


# ══════════════════════════════════════════════
#  MODAL — /boost  (popup libre)
# ══════════════════════════════════════════════
class BoostModal(discord.ui.Modal, title="⚡ Nouvelle fiche boost"):

    champ_titre = discord.ui.TextInput(
        label="Titre",
        placeholder="Ex: Boost x2 — 30 jours",
        required=True,
        max_length=256,
    )
    champ_description = discord.ui.TextInput(
        label="Description",
        placeholder="Décris le boost librement...",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=1024,
    )
    champ_infos = discord.ui.TextInput(
        label="Infos / Prix",
        placeholder="💰 Prix — 2.99€\n⏳ Durée — 30 jours\n🖥️ Serveur — ...",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=1024,
    )
    champ_image = discord.ui.TextInput(
        label="URL de l'image (optionnel)",
        placeholder="https://...",
        required=False,
    )
    champ_btn = discord.ui.TextInput(
        label="Texte du bouton de commande",
        placeholder="Ex: ⚡ Commander",
        required=True,
        max_length=80,
        default="⚡ Commander",
    )

    def __init__(self, salon, couleur):
        super().__init__()
        self.salon   = salon
        self.couleur = couleur

    async def on_submit(self, interaction: discord.Interaction):
        try:
            color = discord.Color.from_str(self.couleur) if self.couleur else discord.Color.from_str("#FF73FA")
        except Exception:
            color = discord.Color.from_str("#FF73FA")

        desc2 = self.champ_description.value.strip() or None
        embed = discord.Embed(
            title       = self.champ_titre.value,
            description = desc2,
            color       = color,
        )
        if self.champ_infos.value.strip():
            embed.add_field(name="\u200b", value=self.champ_infos.value, inline=False)
        if self.champ_image.value.strip():
            embed.set_image(url=self.champ_image.value.strip())
        embed.set_footer(text=CONFIG.get("owner_name", "Boutique"), icon_url=bot.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        view   = BoutonTicket(type_ticket="boost", label_btn=self.champ_btn.value, resume=self.champ_titre.value)
        target = self.salon or interaction.channel
        await target.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Fiche boost envoyée !", ephemeral=True)
        await interaction.response.send_message("✅ Fiche boost envoyée !", ephemeral=True)


# ══════════════════════════════════════════════
#  MODAL — /annonce  (popup libre)
# ══════════════════════════════════════════════
class AnnonceModal(discord.ui.Modal, title="📢 Nouvelle annonce"):

    champ_titre = discord.ui.TextInput(
        label="Titre",
        placeholder="Ex: 🔥 Nouvelle mise à jour !",
        required=True,
        max_length=256,
    )
    champ_contenu = discord.ui.TextInput(
        label="Contenu",
        placeholder="Écris ton annonce ici...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=3000,
    )
    champ_image = discord.ui.TextInput(
        label="URL image (optionnel)",
        placeholder="https://...",
        required=False,
    )

    def __init__(self, salon, mention):
        super().__init__()
        self.salon   = salon
        self.mention = mention

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(color=discord.Color.from_str(CONFIG["embed_color"]))
        embed.add_field(name=self.champ_titre.value, value="\u200b", inline=False)
        embed.add_field(name="\u200b", value=self.champ_contenu.value, inline=False)
        if self.champ_image.value.strip():
            embed.set_image(url=self.champ_image.value.strip())
        embed.set_footer(text=f"Annonce de {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        target  = self.salon or interaction.channel
        content = self.mention if self.mention != "none" else None
        await target.send(content=content, embed=embed)
        await interaction.response.send_message("✅ Annonce envoyée !", ephemeral=True)


# ══════════════════════════════════════════════
#  EVENTS
# ══════════════════════════════════════════════
@bot.event
async def on_ready():
    print(f"✅  {bot.user} connecté ({bot.user.id})")
    acts = {
        "playing":   discord.Game(name=CONFIG["status_text"]),
        "watching":  discord.Activity(type=discord.ActivityType.watching,  name=CONFIG["status_text"]),
        "listening": discord.Activity(type=discord.ActivityType.listening, name=CONFIG["status_text"]),
        "streaming": discord.Streaming(name=CONFIG["status_text"], url=CONFIG.get("stream_url", "")),
        "competing": discord.Activity(type=discord.ActivityType.competing, name=CONFIG["status_text"]),
        "custom":    discord.CustomActivity(name=CONFIG["status_text"]),
    }
    sm = {"online": discord.Status.online, "idle": discord.Status.idle, "dnd": discord.Status.dnd, "invisible": discord.Status.invisible}
    await bot.change_presence(activity=acts.get(CONFIG["status_type"]), status=sm.get(CONFIG["presence"], discord.Status.online))
    bot.add_view(BoutonFermerTicket())
    try:
        synced = await bot.tree.sync()
        print(f"🔄  {len(synced)} commande(s) sync")
    except Exception as e:
        print(f"❌  {e}")


@bot.event
async def on_member_join(member):
    ch = bot.get_channel(CONFIG.get("welcome_channel_id") or 0)
    if not ch:
        return
    embed = discord.Embed(color=discord.Color.from_str(CONFIG["embed_color"]))
    embed.add_field(name=f"👋 Bienvenue {member.display_name} !", value=CONFIG.get("welcome_message", ""), inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"{member.guild.name} • {member.guild.member_count} membres")
    await ch.send(embed=embed)


# ══════════════════════════════════════════════
#  COMMANDES
# ══════════════════════════════════════════════
@bot.tree.command(name="compte", description="🧾 Crée une fiche compte (popup)")
@app_commands.describe(couleur="Couleur hex ex: #FF5733", salon="Salon cible")
@app_commands.checks.has_permissions(manage_messages=True)
async def compte_command(interaction: discord.Interaction, couleur: str | None = None, salon: discord.TextChannel | None = None):
    await interaction.response.send_modal(CompteModal(salon=salon, couleur=couleur or ""))


@bot.tree.command(name="boost", description="⚡ Crée une fiche boost (popup)")
@app_commands.describe(couleur="Couleur hex ex: #FF73FA", salon="Salon cible")
@app_commands.checks.has_permissions(manage_messages=True)
async def boost_command(interaction: discord.Interaction, couleur: str | None = None, salon: discord.TextChannel | None = None):
    await interaction.response.send_modal(BoostModal(salon=salon, couleur=couleur or ""))


@bot.tree.command(name="annonce", description="📢 Crée une annonce (popup)")
@app_commands.describe(mention="Mentionner ?", salon="Salon cible")
@app_commands.choices(mention=[
    app_commands.Choice(name="@everyone", value="@everyone"),
    app_commands.Choice(name="@here",     value="@here"),
    app_commands.Choice(name="Aucune",    value="none"),
])
@app_commands.checks.has_permissions(manage_messages=True)
async def annonce_command(interaction: discord.Interaction, mention: str = "none", salon: discord.TextChannel | None = None):
    await interaction.response.send_modal(AnnonceModal(salon=salon, mention=mention))


@bot.tree.command(name="sondage", description="📊 Lance un sondage")
@app_commands.describe(question="La question", salon="Salon cible")
@app_commands.checks.has_permissions(manage_messages=True)
async def sondage_command(interaction: discord.Interaction, question: str, salon: discord.TextChannel | None = None):
    embed = discord.Embed(color=discord.Color.from_str(CONFIG["embed_color"]))
    embed.add_field(name="📊 Sondage", value="\u200b", inline=False)
    embed.add_field(name="\u200b", value=f"**{question}**", inline=False)
    embed.add_field(name="\u200b", value="👍 Oui  ·  👎 Non", inline=False)
    embed.set_footer(text=f"Sondage de {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    embed.timestamp = discord.utils.utcnow()
    target = salon or interaction.channel
    msg = await target.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")
    await interaction.response.send_message("✅ Sondage lancé !", ephemeral=True)


@bot.tree.command(name="statut", description="🎮 Change le statut du bot")
@app_commands.describe(type_activite="Type", texte="Texte", presence="Présence")
@app_commands.choices(
    type_activite=[
        app_commands.Choice(name="🎮 Joue à",      value="playing"),
        app_commands.Choice(name="👁️ Regarde",     value="watching"),
        app_commands.Choice(name="🎵 Écoute",       value="listening"),
        app_commands.Choice(name="🏆 Participe à",  value="competing"),
        app_commands.Choice(name="✏️ Personnalisé", value="custom"),
    ],
    presence=[
        app_commands.Choice(name="🟢 En ligne",       value="online"),
        app_commands.Choice(name="🟡 Absent",          value="idle"),
        app_commands.Choice(name="🔴 Ne pas déranger", value="dnd"),
        app_commands.Choice(name="⚫ Invisible",       value="invisible"),
    ],
)
@app_commands.checks.has_permissions(administrator=True)
async def statut_command(interaction: discord.Interaction, type_activite: str, texte: str, presence: str = "online"):
    acts = {
        "playing":   discord.Game(name=texte),
        "watching":  discord.Activity(type=discord.ActivityType.watching,  name=texte),
        "listening": discord.Activity(type=discord.ActivityType.listening, name=texte),
        "competing": discord.Activity(type=discord.ActivityType.competing, name=texte),
        "custom":    discord.CustomActivity(name=texte),
    }
    sm = {"online": discord.Status.online, "idle": discord.Status.idle, "dnd": discord.Status.dnd, "invisible": discord.Status.invisible}
    await bot.change_presence(activity=acts.get(type_activite), status=sm.get(presence, discord.Status.online))
    embed = discord.Embed(title="✅ Statut mis à jour", color=discord.Color.green())
    embed.add_field(name="Type", value=type_activite, inline=True)
    embed.add_field(name="Texte", value=texte, inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="aide", description="📖 Liste des commandes")
async def aide_command(interaction: discord.Interaction):
    embed = discord.Embed(color=discord.Color.from_str(CONFIG["embed_color"]))
    embed.add_field(name="📖 Commandes", value="\u200b", inline=False)
    embed.add_field(
        name="\u200b",
        value=(
            "`/compte` — Fiche compte + ticket\n"
            "`/boost` — Fiche boost + ticket\n"
            "`/annonce` — Annonce\n"
            "`/sondage` — Sondage 👍/👎\n"
            "`/statut` — Changer le statut *(Admin)*\n"
            "`/aide` — Cette page"
        ),
        inline=False,
    )
    embed.set_footer(text=CONFIG.get("owner_name", "Bot"), icon_url=bot.user.display_avatar.url)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    msg = "❌ Permissions insuffisantes." if isinstance(error, app_commands.MissingPermissions) else f"❌ `{error}`"
    try:
        await interaction.response.send_message(msg, ephemeral=True)
    except discord.InteractionResponded:
        await interaction.followup.send(msg, ephemeral=True)


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN") or CONFIG.get("token")
    if not token:
        raise ValueError("❌ DISCORD_TOKEN manquant !")
    bot.run(token)
