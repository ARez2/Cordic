import sqlite3
from sqlite3 import Error
import os

from src.lib.utils import COLOR_GREEN

#sqlite3
class jiradatabase():
    def __init__(self):
        self.con = None
        self.filename = "database.db"
        self.path = "database.db"#os.path.join(os.path.dirname(__file__), self.filename)
        #self.path = "src/command_clients/" + self.filename
        self._create_connection()
    
    #baut eine Verbindung zur Datenbank-Datei auf
    def _create_connection(self):
        try:
            self.con = sqlite3.connect(self.path)
        except Error as e:
            print(e)

        self.cur = self.con.cursor()
        self.setup_tables()

        #if os.path.getsize(os.path.join(os.path.dirname(__file__), self.filename)) == 0:
        #    self.setup_tables()

    #erstellt tabellen, falls nicht vorhanden
    def setup_tables(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS users
               (dcuserID text PRIMARY KEY, jiraemail text, jiratoken text, jiraaccountid text)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS domain
               (domainname text PRIMARY KEY)''')
        self.con.commit()


    #trägt die Discord und Jira Nutzerdaten in die Datenbank ein und übergibt das Embed
    def connect_user(self, dcuserID, jiraemail, jiratoken, jiraaccountid):
        #command = f"REPLACE INTO users VALUES('{dcusername}', '{jiraemail}', '{jiratoken}', '{jiraaccountid}')"
        command = "REPLACE INTO users VALUES(?, ?, ?, ?)"
        self.cur.execute(command, (dcuserID, jiraemail, jiratoken, jiraaccountid))
        self.con.commit()
        embedstructure = {
            "title": "Connect User",
            "description": f"Der Nutzer <@!{dcuserID}> wurde erfolgreich mit seinem Jira-Account verknüpft",
            "fields": None,
            "color": 0x2ecc71
        }
        return embedstructure

    #ändert die Domain in der Tabelle domain
    def init_domain(self, domain):
        command = "DELETE FROM domain"
        self.cur.execute(command)
        self.con.commit()
        command = "INSERT INTO domain VALUES(?)"
        self.cur.execute(command, (domain,))
        self.con.commit()
        embedstructure = {
            "title": "Init Domain",
            "description": f"Die Domain wurde erfolgreich initialisiert",
            "fields": None,
            "color": COLOR_GREEN
        }
        return embedstructure

    #übergibt den domainnamen
    def get_domain(self):
        self.setup_tables()
        command = f"SELECT domainname FROM domain"
        self.cur.execute(command)
        row = self.cur.fetchone()
        if row != None:
            return row[0]
        else:
            return None

    #übergibt die jira-email von einem Discord-Nutzer
    def get_user_email(self, dcuserID):
        command = f"SELECT jiraemail FROM users WHERE dcuserID = ?"
        self.cur.execute(command, (dcuserID,))
        row = self.cur.fetchone()
        if row != None:
            return row[0]
        else:
            return None

    #übergibt den Jira-Token von einem Discord-Nutzer
    def get_user_jiratoken(self, dcuserID):
        command = f"SELECT jiratoken FROM users WHERE dcuserID = ?"
        self.cur.execute(command, (dcuserID,))
        row = self.cur.fetchone()
        if row != None:
            return row[0]
        else:
            return None

    #übergibt die jiraAccountID von einem Discord-Nutzer
    def get_user_jiraaccountid(self, dcuserID):
        command = f"SELECT jiraaccountid FROM users WHERE dcuserID = ?"
        self.cur.execute(command, (dcuserID,))
        row = self.cur.fetchone()
        if row != None:
            return row[0]
        else:
            return None
    
    #überprüft, ob ein Discord-Nutzer in der Datenbank existiert
    def user_exist(self, dcuserID):
        command = f"SELECT * FROM users WHERE dcuserID = ?"
        self.cur.execute(command, (dcuserID,))
        row = self.cur.fetchone()
        return row != None