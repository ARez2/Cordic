import nextcord
from nextcord.ext import commands
from nextcord import Embed, Intents

GUILD_IDS = [908740156306112512]

class DiscordChannel(commands.Cog):
    bot = None

    def __init__(self) -> None:
        if DiscordChannel.bot is None:
            intents = Intents.default()
            intents.members = True
            DiscordChannel.bot = commands.AutoShardedBot(command_prefix="j!", intents=intents)
            @self.bot.event
            async def on_ready():
                print(f'{self.bot.user} has logged in.')

            try:
                self.bot.add_cog(self)
            except Exception as e:
                print(f"An error has occured when trying to add {self} as Cog: {e}")

    def run(self, token):
        self.bot.run(token)

    def register_slash_command(self, callback):
        # bot.slash_command erstellt einen Dekorator um unsere Funktion (unsere Funktion = callback)
        # Dieser Dekorator erweitert unsere Funktion um Nextcord Slash Cmd Logik
        decorator = self.bot.slash_command(guild_ids=GUILD_IDS)
        # Wir müssen den Dekorator auch mit unserer Funktion (=callback) aufrufen, damit intern in
        # Nextcord eine Instanz von 'ApplicationCommand' erstellt wird, welche sich als Attribut
        # unser Callback merkt. Wenn dieser ApplicationCommand von Nextcord aufgerufen wird,
        # wird unsere Funktion mit den Args (welche ApplicationCommand mitgegeben wurden) aufgerufen
        application_command = decorator(callback)

    def register_user_command(self, name: str, callback):
        self.bot.user_command(guild_ids=GUILD_IDS)(callback)

    def register_message_command(self, callback, **kwds):
        self.bot.message_command(**kwds)(callback)

    def cog_unload(self):
        self.bot.slash.remove_cog_commands(self)

    def embed_from_dict(self, _dict):
        e = Embed()
        e.title = _dict.get("title")
        e.description = _dict.get("description")
        e.colour = _dict.get("color") or 0x36393F
        if _dict.get("fields") is not None:
            for key in _dict.get("fields", []):
                if isinstance(_dict["fields"][key], list):
                    delimiter = "\n"
                    part = delimiter.join(_dict["fields"][key])
                    e.add_field(name=key, value=part)
                else:
                    e.add_field(name=key, value=_dict["fields"][key])
        return e
