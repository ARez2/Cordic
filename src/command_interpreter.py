from command_clients.general import GeneralClient
from command_clients.jira import JiraClient
from command_clients.termin import TerminClient
from command_clients.debug import DebugClient
import time
from datetime import timedelta
from lib import utils
import json

from lib.utils import COLOR_RED, COLOR_GREEN, COLOR_BLUE


class CommandInterpreter():
    def __init__(self) -> None:
        self.clients = {}
        self.register_client("general", GeneralClient(), ["general", "g"])
        self.register_client("jira", JiraClient(), ["jira", "j"])
        self.register_client("event", TerminClient(), ["event", "e"])
        self.register_client("debug", DebugClient(), ["dbg", "debug"])


    def register_client(self, name, client, keywords):
        if name in self.clients:
            return

        self.clients[name] = {
            "client": client,
            "keywords": keywords,
        }


    async def receive_input(self, command_type, command, arguments, user, channel, guild, bot):
        if arguments is not None:
            arguments = arguments.split(" ")
        target_client = None
        for c in self.clients:
            if command_type in self.clients[c]["keywords"]:
                command_type = c
                target_client = self.clients[c]["client"]
                break
        
        embedstructure = {
            "title": "Error",
            "description": "Could not find command: Maybe you are missing ´t`/´termin` or ´j`/´jira` or ´g`/`general`?",
            "fields": None,
            "color": COLOR_RED
        }
        output = embedstructure

        if target_client is None:
            return output
        
        if command_type == "general":
            output = await self.handle_general_commands(target_client, command, arguments, user, guild)
        elif command_type == "debug":
            target_client.init_bot(bot)
            output = await self.handle_debug_commands(target_client, command, arguments, user, guild)
        elif command_type == "jira":
            output = self.handle_jira_commands(target_client, command, arguments, user)
        elif command_type == "event":
            output = self.handle_event_commands(target_client, command, arguments, user, channel)

        return output


    async def handle_general_commands(self, client : GeneralClient, command, args, user, guild):
        if command == "setup":
            # args: domain name (jira)
            if args is None or len(args) <= 0:
                return {
                    "title": "ERROR",
                    "description": "Missing Arguments!",
                    "color": COLOR_RED
                }
            return await client.setup(args, user, guild, self.clients["jira"]["client"])


    def handle_jira_commands(self, client: JiraClient, command, args, user):
        try:
            connect_kw = ["connect_user", "connect"]
            initdomain_kw = ["setup_domain", "domain"]
            userissues_kw = ["issues_by_user", "issues", "userissues"]
            issuedetails_kw = ["issue_details", "details"]
            projects_kw = ["projects"]
            userprojects_kw = ["projects_by_user", "userprojects"]
            comment_kw = ["comment_on", "comment"]
            if command in connect_kw:
                if args is None or len(args) < 3:
                    return {
                        "title": "ERROR",
                        "description": "Missing Arguments!",
                        "color": COLOR_RED
                    }
                else:
                    return client.connect_user({
                        "dc_user": user,
                        "email": args[0],
                        "jiratoken": args[1],
                        "account_id": args[2],
                    })
            elif command in initdomain_kw:
                if args is None:
                    return {
                        "title": "ERROR",
                        "description": "Missing Arguments!",
                        "color": COLOR_RED
                    }
                else:
                    return client.setup_domain(args[0])
            elif command in userissues_kw:
                if args is not None:
                    target_user_id = args[0]
                    target_user_id = target_user_id.replace("<@!", "")
                    target_user_id = target_user_id.replace(">", "")
                    user = {
                        "id": target_user_id
                    }
                    return client.get_issues_by_user(user)
                else:
                    return client.get_issues_by_user(user)
            elif command in issuedetails_kw:
                if args is None:
                    return {
                        "title": "ERROR",
                        "description": "Missing Arguments!",
                        "color": COLOR_RED
                    }
                else:
                    return client.get_issue_details(user, args[0])
            elif command in projects_kw:
                return client.get_all_projects(user)
            elif command in userprojects_kw:
                if args is not None:
                    target_user_id = args[0]
                    target_user_id = target_user_id.replace("<@!", "")
                    target_user_id = target_user_id.replace(">", "")
                    user = {
                        "id": target_user_id
                    }
                    return client.get_projects_by_user(user)
                else:
                    return client.get_projects_by_user(user)
            elif command in comment_kw:
                if args is not None and len(args) > 1:
                    return client.comment_on(user, args[0], " ".join(args[1:]))
                else:
                    return {
                        "title": "ERROR",
                        "description": "Missing Arguments!",
                        "color": COLOR_RED
                    }
            elif command == "help":
                return {
                    "title": "Jira Commands",
                    "description": "Interact with a Jira Project through Discord \n Usage: `/cordic j [CMD] [**OPTIONS/ARGS]`",
                    "fields": {
                        "`connect_user` | `connect`": "Connects a users jira account to its discord account \n args: `email jira_api_token jira_account_id`",
                        "`setup_domain` | `domain`": "Setup the domain name of your Jira Cloud Instance \n args: `domain`",
                        "`issues_by_user` | `issues` | `userissues`": "Shows all issues of yourself or user when specified in args \n args: [optional] `ping or dcID`",
                        "`issue_details` | `details`": "Shows the details displayed in jira for one specific ticket \n args: `issue_name`",
                        "`projects`": "Returns all projects where the user has a task",
                        "`projects_by_user` | `userprojects`": "Return all running Projects by a user \n args: [optional] `ping or dcID`",
                        "`comment_on` | `comment`": "Leave a comment under an issue \n args: `issuekey comment`",
                        "`Reference`": "There is a difference between `issuename` and `issuekey`. Structure issuekey: projectname-number /n If the Bot does not react, then connect again /n the domain is like this 'cordic'"
                    },
                    "color": COLOR_GREEN
                }
        except Exception as e:
            return {
                "title": "Error: Jira",
                "description": f"Invalid command or argument(s): {e}",
                "fields": None,
                "color": COLOR_RED
            }

        return {
            "title": "Error: Jira",
            "description": "Could not find command",
            "fields": None,
            "color": COLOR_RED
        }


    def handle_event_commands(self, client: TerminClient, command, args, user, channel):
        try:
            create_kw = ["create", "cre"]
            select_kw = ["select", "sel"]
            delete_kw = ["delete", "del"]
            if command in create_kw:
                if len(args) < 4:
                    args[4] = ""
                if len(args) < 5:
                    args[5] = 6
                ev = client._addEvent(
                    args[0],
                    args[1],
                    utils.extract_text_from_quotes(" ".join(args)),
                    utils.extract_text_from_quotes(" ".join(args),"'"),
                    6,
                    channel.id
                )
                client._addUserToEvent(user.id, channel.guild.id, ev.id)
                return {"title": "Event created!", "color": COLOR_GREEN, "description": f"Event-IDD: {ev.id}"}
            elif command in select_kw:
                if len(args) > 0:
                    item = client._fetchEvent(args[0])
                    if not item:
                        return {
                            "description": f"Error: That ID ({args[0]}) is not there (Or did not return a valid Response).\nMind, that the IDs are Case-sensitive"
                        }
                    return {
                        "description": "Event-Details",
                        "color": COLOR_GREEN,
                        "fields": {
                            "Date": f"<t:{item.timestamp}> (<t:{item.timestamp}:R>)",
                            "Name": item.name,
                            "Description": item.description,
                            "IDD": item.id,
                            "Custom message": item.message
                        }
                    }
                else:
                    return {"description": "No ID specified", "color": COLOR_RED}
            elif command in delete_kw:
                if len(args) > 0:
                    item = client._fetchEvent(args[0])
                    if not item:
                        return {
                            "description": f"Error: That ID ({args[0]}) is not there (Or did not return a valid Response).\nMind, that the IDs are Case-sensitive and will be deleted *instantly* after the Event Start"
                        }
                    client._deleteEvent(args[0])
                    return {"description": f'{item.name} has been deleted!', "color": COLOR_GREEN}
                else:
                    return {"description": "No ID specified!", "color": COLOR_RED}
            elif command == "help":
                return {
                    "title":"Event commands for Cordic",
                    "description":"Create/View/Delete Events \n Usage: `/cordic e [CMD] [**OPTIONS/ARGS]` \n",
                    "fields": {
                            "`help`": "Shows this menu",
                            "`create` | `cre`": "Create event args: `Date Name Description Extra_Message:Optional ID-Length:Optional`",
                            "`select` | `sel`": "View event \n args: `ID`",
                            "`delete` | `del`": "Delete event \n args: `ID`",
                            "`join`": "Subscribe to an Event \n args: `ID`",
                        },
                    "color":COLOR_GREEN}

            elif command == "join":
                if len(args) > 0:
                    item = client._fetchEvent(args[0])
                    if not item:
                        return {
                            "description": f"Error: That ID ({args[0]}) is not there (Or did not return a valid Response).\nMind, that the IDs are Case-sensitive"
                        }
                    client._addUserToEvent(user.id, channel.guild.id, args[0])

                    return {"description": f'You subscribed to {item.name}!', "color": COLOR_GREEN}
                else:
                    return {"description": "No ID specified!", "color": COLOR_RED}


        except Exception as e:
            return {"description": f"Invalid command or argument(s): {e}", "color": COLOR_RED}

        return {"description": f"Invalid command: {e}", "color": COLOR_RED}

    
    async def handle_debug_commands(self,client:DebugClient, command, args, user, channel):
        try:
            if command == "show_info":
                statistics = await client.get_general_stats()
                
                return {
                    "title":"Displaying Debug Infos",
                    "description":"...",
                    "fields": {
                            "Uptime": str(timedelta(seconds=int(round(time.time()-statistics["uptime"])))),
                            "Discord API Latency": round(statistics["latency"]),
                            "Events:Running": ", ".join(e.id for e in statistics["events"]["running"]) or "Null",
                            "Events:Open": ", ".join(e.id for e in statistics["events"]["open"]) or "Null",
                            "Errors":",".join(statistics["errors"])
                        },
                    "color":COLOR_GREEN}
        except Exception as e:
            return {"description": f"Invalid command or argument(s): {e}", "color": COLOR_RED}

        return {"description": f"Invalid command: {command}", "color": COLOR_RED}
