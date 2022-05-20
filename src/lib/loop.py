from nextcord.ext import tasks
import asyncio


@tasks.loop(seconds=20)
async def _e_client_start(cls, httpclient):
    events = cls._checkAllEvents()
    running = []
    for i in events:
        if i[1] == "running":
            running.append(i[0])
    for r in running:
        print(vars(r))
        await httpclient.bot.get_channel(int(r.channel)).send(
            embed=httpclient.embed_from_dict({
                "title": "🔔 Event!",
                "description": r.description,
                "fields": {
                    "Name": r.name,
                    "Custom Message": r.message if r.message != '' else 'Null'
                }
            })
        )
        for user in r.users:
            u = await httpclient.bot.fetch_user(int(user.userid_guildid.split("@")[0]))
            
            await u.send(embed=httpclient.embed_from_dict({
                "title": "🔔 Event!",
                "description": r.description,
                "fields": {
                    "Name": r.name,
                    "Custom Message": r.message,
                    "On": httpclient.bot.get_guild(int(user.userid_guildid.split("@")[1])).name
                }
            }))
