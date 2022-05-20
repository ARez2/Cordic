# DiscordManagementBot

## Installation
* Repository von Github clonen.
* In src\lib\discord_channel.py die GUILD_IDS (= Server ID, auf dem der Bot verwendet wird) Variable entsprechend bearbeiten

### Tokens
Der Discord API Token wird über das Discord Developer Portal (https://discord.com/developers/) erstellt und in der ``bottoken.token`` Datei eingegeben. Dieser Token wird dann beim Ausführen des Bots ausgelesen. Außerdem steht die ``bottoken.token`` Datei im .gitignore, sodass sie nicht auf GitHub hochgeladen wird.

#### Jira
Um auf seine Jira Account ID zuzugreifen, loggt man sich zunächst auf Atlassian.com ein und wählt dann den Jira Work Management Punkt aus. Daraufhin kann man oben rechts bei seinem Profilbild klicken und auf "Profil" gehen. Dann sieht man in der URL seinen Token (letzter Teil der URL).

#### Github
Eventuell vorher einen "Personal Access Token" anlegen. Dafür unter GitHub Profil - Einstellungen - Developer Settings - Personal Access Tokens
einen neuen Token erstellen (am besten mit "Never expire")



### Repo installieren

    cd <Projektordner>
    git clone https://github.com/ARez2/DiscordManagementBot.git
    cd DiscordManagementBot


Venv anlegen und aktivieren
    
    python -m venv venv
    venv\Scripts\activate


Alle benötigten Module installieren

    pip install -r requirements.txt

## .ENV Anlegen

In einer .env-Datei folgenden Code schreiben:

    DISCORD_TOKEN=<Euer Token>

## Bot ausführen
   
    cd <Projektordner>\DiscordManagementBot
    
    # Für Windows:
    venv\Scripts\activate
    # Für Linux
    . venv\bin\activate
    
    python cordic.py
