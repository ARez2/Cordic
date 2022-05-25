import nextcord
from nextcord import SlashOption, PermissionOverwrite
from lib.discord_channel import DiscordChannel
from command_clients.termin import TerminClient
from lib.loop import _e_client_start as eventLoop
import json
import time

class Text(DiscordChannel):
    SENSITIVE_COMMANDS = ["connect_user"]
    
    def __init__(self, input_callback) -> None:
        super().__init__()
        
        async def test(interaction:nextcord.Interaction, user:nextcord.Member):
            await interaction.response.send_message(user.mention)
        self.input_callback = input_callback
        
        # Fügt automatisch noch argumente wie z.b. guild_id=[...] hinzu
        self.register_slash_command(self.cordic)
        self.register_user_command("reeeee",test)
        @self.bot.event
        async def on_ready():
            self.bot.uptime = time.time()
            await self.bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching,name="the Gears turn..."))
            await eventLoop.start(cls=TerminClient(),httpclient=self)


    async def cordic(self,
        ctx,
        command_type : str = SlashOption(name="command_type",
                                        description="Wether command is a jira or event command",
                                        required=True,
                                        choices={
                                            "Cordic general commands": "general",
                                            "jira/ j": "jira",
                                            "event/ e": "event",
                                            "debug /dbg":"debug"
                                            }
                                        ),
        command : str = SlashOption(name="command",
                                    description="Command to run",
                                    required=True,
                                    choices={
                                        "GENERAL_setup": "setup",
                                        "GENERAL_help": "help",

                                        "JIRA_help": "help",
                                        "JIRA_connect_user": "connect_user",
                                        "JIRA_setup_domain": "setup_domain",
                                        "JIRA_issues_by_user": "issues_by_user",
                                        "JIRA_issue_details": "issue_details",
                                        "JIRA_projects": "projects",
                                        "JIRA_projects_by_user": "projects_by_user",
                                        "JIRA_comment_on": "comment_on",
                                        "EVENT_help": "help",
                                        "EVENT_create": "create",
                                        "EVENT_select": "select",
                                        "EVENT_join": "join",
                                        "EVENT_delete": "delete",
                                        
                                        "DEBUG_ShowInfo": "show_info",
                                        }
                                    ),
        arguments : str = SlashOption(name="args",
                                        description="Look into the command types help list for a list of arguments",
                                        required=False)):
        
        output_data = await self.input_callback(command_type, command, arguments, ctx.user, ctx.channel, ctx.guild,self.bot)
        
        # Convert to json object for easier access
        if isinstance(output_data,str):
            output_data = json.loads(output_data)
        
        #embed= self.embed_from_dict(output_data)
        await ctx.send(embed=self.embed_from_dict(output_data), ephemeral=command in self.SENSITIVE_COMMANDS)      