# ══════════════════════════════════════════════════════════
#  config.py  —  Tout se personnalise ici !
# ══════════════════════════════════════════════════════════

CONFIG = {

    # ── TOKEN ─────────────────────────────────
    # Laisse vide si tu utilises Railway (variable d'env)
    "token": "",

    # ── PRÉFIXE ───────────────────────────────
    "prefix": "!",

    # ── STATUT ────────────────────────────────
    # type : "playing" | "watching" | "listening" | "streaming" | "competing" | "custom"
    "status_type": "streaming",
    "status_text": "Woxoo Market 🛒",
    "stream_url":  "https://twitch.tv/discord",
    # Présence : "online" | "idle" | "dnd" | "invisible"
    "presence":    "online",

    # ── COULEUR DES EMBEDS ────────────────────
    # Couleurs sympas :
    #   "#5865F2" Bleu Discord  |  "#57F287" Vert
    #   "#FF73FA" Rose/Boost    |  "#FEE75C" Jaune
    #   "#ED4245" Rouge         |  "#EB459E" Rose vif
    "embed_color": "#5865F2",

    # ── INFOS ─────────────────────────────────
    "owner_name":      "Woxoo",
    "bot_description": "Woxoo",

    # ── TICKETS ───────────────────────────────
    # ID du rôle Staff (clic droit sur le rôle → Copier l'ID)
    # Met None si tu veux pas de rôle staff spécifique
    "1490444529164357905":   None,     # ex: 1234567890123456789

    # Nom de la catégorie où seront créés les tickets
    "ticket_category": "📩 TICKETS",

    # Temps de réponse affiché dans le ticket
    "response_time":   "< 24h",

    # ── BIENVENUE ─────────────────────────────
    # ID du salon de bienvenue (ou None pour désactiver)
    "welcome_channel_id": None,  # ex: 1234567890123456789
    "welcome_message":    "Bienvenue ! Consulte les règles 📜",

}
