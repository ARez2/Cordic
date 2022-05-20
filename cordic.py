import sys
import os
import logging
import faulthandler
from dotenv import load_dotenv as _load_dotenv
import typing as t
from pathlib import Path

faulthandler.enable()

for item in sys.argv:
  if item == "--logging=true":
    logging.basicConfig(format='[%(asctime)s] %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from text import Text
from command_interpreter import CommandInterpreter


class Cordic():
    cmd_interpreter = None
    def __init__(self,**kwds) -> None:
        self.load_tokens(**kwds)
        self.cmd_interpreter = CommandInterpreter()
        self.text = Text(self.input_callback)

    async def input_callback(self, command_type, command, input_data, user, channel, guild,bot):
        return await self.cmd_interpreter.receive_input(command_type, command, input_data, user, channel, guild,bot)


    def run(self):
        self.text.run(self.discordtoken)    

    def load_tokens(self,*,path="bottoken.token",load_dotenv:bool=True,dotenv_path:t.Union[str,os.PathLike]=".env"):
        def load_token(filename: str):
            tokenfilename = os.path.join(os.path.dirname(__file__), filename)
            with open(tokenfilename, "r") as file:
                return file.readline()

        if not load_dotenv:
            self.discordtoken = load_token(Path(".") / path)
        else:
            _load_dotenv(dotenv_path)
            self.discordtoken = os.getenv("DISCORD_TOKEN")



if __name__ == "__main__":
    cordic = Cordic()
    cordic.run()
