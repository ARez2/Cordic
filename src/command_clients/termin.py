import re
import os
import random
import string
from multidict import CIMultiDict
from src.lib.utils import Termine,t_base,t_engine, webhook, DiscordUser
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

_session = sessionmaker(t_engine)

class TerminClient():
    def __init__(self,**kwds):
        """
        The __init__ function is called automatically when a class is instantiated. 
        It can take arguments, some of which are keywords and others of which are 
        positional arguments. It can also take named arguments, sometimes called kwargs.
        
        :param self: Refer to the instance of the class
        :param **kwds: Pass a dictionary of keyword arguments to the function
        """
        self.kwds = kwds
        self._installDatabase()
        self.db = _session()                
    
    def _installDatabase(self):
        try:
            Termine.query.all()

        except:
            t_base.metadata.create_all(t_engine)

    def _getRandomString(self,max_len:int):
    
        """ Return a Random String of ASCII Chars
        :param self: Refers to the Class
        :param max_len:int:
    
        :raises:
        """    
        letters = string.ascii_lowercase+string.ascii_uppercase+string.digits
        result_str = ''.join(random.choice(letters) for i in range(max_len))
        return result_str
    
    def _addEventBase(self,idx,name,timestamp,description,message,channel):
        tr = Termine(name,timestamp,description,message,channel,idx,[])
        self.db.add(tr)
        webhook("https://discord.com/api/webhooks/953737526571573279/kQ46eKnoNpxIC2uy7r-bYXzN-jr7p8vww2mR-xnaZrVpDnuBHLrRV2UI4GVyxJ3v0LmL",title="\✔ Event added",description=f"{name} has been added to the Database",fields=[{"name":"ID","value":idx},{"name":"Timestamp","value":f"<t:{timestamp}:R>"}])
        self.db.commit()
        return tr

    def _addUserToEvent(self, user_id, guild_id, event_id):
        event = self._fetchEvent(event_id)
        u = DiscordUser(userid_guildid = f'{user_id}@{guild_id}', event = event)
        self.db.add(u)
        self.db.commit()


    def _addEvent(self,date,name,description,custom_message=None,id_length:int=6,channel:int=0):
        """
        The _addEvent function adds an event to the calendar.
        It takes a date, name, description and custom_message as arguments.
        The id of the event is generated automatically from random characters and can be accessed by calling tr._getEventId(event).
        The channel argument specifies which channel should be used for notifications
        
        :param self: Access the class attributes
        :param date: Set the date of the event
        :param name: Set the name of the event
        :param description: Describe the event
        :param custom_message=None: Add a custom message to the event
        :param id_length:int=6: Set the length of the id
        :param channel:int=0: Specify the channel where the event should be added
        :return: The variable tr
        """
        assert self._matchDateFormat(date), "Date doesn't fit DD.MM.YYYY-HH:MM:SS Format"
        date_object = datetime.strptime(date,"%d.%m.%Y-%H:%M:%S")
        idd = self._getRandomString(int(id_length))
        tr = self._addEventBase(idd,name,round(date_object.timestamp()),description,custom_message,channel)
        return tr
    
    def _fetchEvent(self,idd):
        tr = self.db.query(Termine).filter(Termine.id==idd).first()
        return tr
     
    def _matchDateFormat(self,date):
        """
        The _matchDateFormat function checks if the date is in a valid format.
        The function takes one argument, date, and returns True if it is in a valid format or False otherwise.
        
        :param self: Reference the class instance
        :param date: Match the date format
        :return: True if the date format is correct
        """
        DATE_REGEX = r"[0123456789][0123456789].[0123456789][0123456789].[0123456789][0123456789][0123456789][0123456789]-[0123456789][0123456789]:[0123456789][0123456789]:[0123456789][0123456789]"
        if re.match(DATE_REGEX,date):
            return True
        return False


    def _checkAllEvents(self):
        """
        The _checkAllEvents function checks all events in the database and returns a tuple containing the event object and a string describing whether it is currently running or not.
        
        
        :param self: Access the class attributes and methods
        :return: A list of tuples containing the event and a string that indicates if it is running or not
        """
        event_list = self.db.query(Termine).all()
        all_open = []
        current_running = []
        for evt in event_list:
            c_evt = evt
            if int(evt.timestamp) < int(datetime.now().timestamp()):
                
                c_evt = evt
                try:
                    self._deleteEvent(c_evt.id)
                except Exception as error:
                    print(error)
                self.db.commit()
                yield (c_evt, "running")
            else:
                yield (evt, "open")
    

    
    def _deleteEvent(self,idd):
        self.db.query(Termine).filter(Termine.id==idd).delete()
        self.db.commit()

if __name__ == "__main__":
    evtClient = TerminClient()
    events = evtClient._checkAllEvents()
    for e, state in events:
        print(f"{e[0].name} is {state}")
