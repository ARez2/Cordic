import sqlite3
from .termin import TerminClient
from src.lib.utils import Error

class DebugClient:
    def __init__(self, bot=None):
        self.bot = bot
        self.conn_evt = sqlite3.connect("termine.db")
        

    def init_bot(self,bot):
        self.bot = bot

    async def get_general_stats(self):
        def errortrace():
            cur = self.conn_evt.execute("SELECT * FROM error;")
            for i in cur.fetchall():
                yield i
        events = TerminClient()._checkAllEvents()
        running = []
        _open = []
        for e in events:
            if e[1] == "running":
                running.append(e[0])
            else:
                _open.append(e[0])
        
        errors = errortrace()
        
        return {
            "latency":self.bot.latency,
            "uptime":self.bot.uptime,
            "events":{
                "running":running,
                "open":_open,
            },
            "errors":errors
        }