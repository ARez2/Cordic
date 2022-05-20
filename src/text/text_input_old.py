import asyncio
from typing_extensions import Required
from nextcord import Embed
from nextcord.ext import commands
from dislash import slash_command, user_command, ActionRow, Button, ButtonStyle, Option, OptionType, ContextMenuInteraction

from ..lib.utils import convert_time


class TextInput(commands.Cog):
    def __init__(self, channel) -> None:
        #super().__init__()
        self.channel = channel

        self.channel.register_slash_command("ping", "Ping!", self.ping)
        
    
    def cog_unload(self):
        self.bot.slash.remove_cog_commands(self)
        pass


    #@slash_command("ping", "Ping!", guild_ids=[908740156306112512], options=[])
    async def ping(self, ctx):
        #await ctx.send(f'Pong! {round(self.bot.latency*1000)}ms')
        await ctx.send(f'Pong!')


    # Example of a slash command in a cog
    @slash_command(description="Says Hello")
    async def hello(self, inter):
        await inter.respond("Hello from cog!")


    @slash_command(name="say",description="Der Bot wiederholt was du sagst", guild_ids=[908740156306112512],options=[
        Option("text", "Der Text der wiederholt wird", OptionType.STRING, True),
        Option("number", "Wie oft der Text wiederholt wird", OptionType.INTEGER, True)
    ])
    async def repeat(self, ctx, *, text:str, number : int):
        for _i in range(number):
            await ctx.send(text)


    @slash_command(name="remindme",description="Der Bot erinnert dich an ein Event. Benutzung: /remindme 1h test", guild_ids=[908740156306112512],options=[
        Option("zeit", "Die Zeit", OptionType.STRING, required=True)
        ,Option("text", "Der Text an den ich dich erinnern soll", OptionType.STRING, required=True)
    ])
    async def remindme(self, ctx,zeit:str,text:str):
        t = convert_time(zeit)
        await ctx.send(f'Ich werde dich in {zeit} and {text} erinnern!',hidden=True)
        await asyncio.sleep(t)
        await ctx.send(f'{ctx.author.mention} {text}')
    

    @user_command(name="Created at", guild_ids=[908740156306112512])
    async def created_at(self, ctx: ContextMenuInteraction):
        # User commands always have only this ^ argument
        await ctx.respond(
            f"{ctx.user} was created at {ctx.user.created_at}",
            ephemeral=True # Make the message visible only to the author
        )
    

    @user_command(name="Press me")
    async def press_me(self, inter):
        # User commands are visible in user context menus
        # They can be global or per guild, just like slash commands
        await inter.respond("Hello there!")


    @commands.command()
    async def buttontest(self, ctx):
        # Create a row of buttons
        row = ActionRow(
            Button(
                style=ButtonStyle.red,
                label="Red pill",
                custom_id="red_pill"
            ),
            Button(
                style=ButtonStyle.blurple,
                label="Blue pill",
                custom_id="blue_pill"
            )
        )
        # Note that we assign a list of rows to components
        msg = await ctx.send("Choose your pill:", components=[row])
        # This is the check for button_click waiter
        def check(inter):
            return inter.author == ctx.author
        # Wait for a button click under the bot's message
        inter = await msg.wait_for_button_click(check=check)

        # Respond to the interaction
        await inter.reply(
            f"Your choice: {inter.clicked_button.label}",
            components=[] # This is how you remove buttons
        )


#def setup(bot):
#	bot.add_cog(TextInput(bot))