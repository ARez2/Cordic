import asyncio
import nextcord
from sqlalchemy import create_engine,Column,Integer,String,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
import requests


COLOR_GREEN = 0x2ecc71
COLOR_RED = 0xe74c3c
COLOR_BLUE = 0x3498db

def extract_text_from_quotes(text:str,seperator:str="\""):
    firstquote = text.find(seperator)
    lastquote = firstquote+1
    quotes = []

    for f in range(len(text)):
        if text[f] == seperator:
                    quotes.append(f)
    return text[quotes[0]+1:quotes[1]]
    

t_engine = create_engine("sqlite:///database.db")

t_base = declarative_base()

def webhook(url,**data):
    r = requests.post(url,json=data)
    r.raise_for_status
    return r

class Termine(t_base):
    __tablename__ = "termine"
    termin_idx = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String)
    timestamp = Column(Integer)
    description = Column(String)
    message = Column(String)
    channel = Column(Integer)
    id = Column(String) 
    def __init__(self, name, timestamp, description, message, channel, id, users):
        self.name = name
        self.timestamp = timestamp
        self.description = description
        self.message = message
        self.channel = channel
        self.id = id
        self.users = users

class DiscordUser(t_base):
    __tablename__ = "discorduser"
    id = Column(Integer, primary_key=True, autoincrement = True)
    userid_guildid = Column(String)#, primary_key=True)
    
    evid = Column(String, ForeignKey('termine.id'))
    event = relationship("Termine", back_populates = 'users', lazy='subquery')

Termine.users = relationship("DiscordUser", order_by=DiscordUser.userid_guildid, back_populates='event', lazy='subquery')

class Error(t_base):
    __tablename__ = "error"
    id = Column(Integer, primary_key=True, autoincrement = True)
    command_triggered = Column(String(20))
    user_id = Column(Integer)
    details = Column(String(3500))


def convert_time(time):
    pos = ["s","m","h","d"]
    time_dict = {"s":1,"m":60,"h":3600,"d":3600*24}
    unit = time[-1]
    
    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]

def _override_database():
    t_base.metadata.create_all(t_engine)        

