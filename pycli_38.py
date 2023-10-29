"""
Python Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Basic librairy for create CLI in Pyth
on.

:copyright: Copyright (c) 2023 Overdjoker048
:license: MIT, see LICENSE for more details.

Create basic Python CLI::

    >>> import PyCLI
    >>> cli = PyCLI.CLI()
    >>> @cli.command()
    >>> def hello_world():
    >>>     print("Hello World")
    >>> cli.run()
"""

__encoding__ = "UTF-8"
__title__ = 'PyCLI'
__author__ = 'Overdjoker048'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2023 Overdjoker048'
__version__ = '1.0'
__all__ = ['CLI', 'echo', 'prompt', 'write_logs']

import time
import inspect
from datetime import datetime
import os
import platform

class CLI:
    def __init__(self,
                 prompt: str = "Python@CLI\\>",
                 not_exist: str = "This command does not exist.\nDo help to get the list of existing commands.",
                 logs: bool = True,
                 animation: bool = True,
                 cooldown: float or int = 0.1,
                 help_cmd: bool = True
                 ) -> None:
        """
        This object allows the creation of the CLI. The prompt parameter defines the 
        text that will be displayed in the terminal to enter the command. The not_exist 
        parameter will define the text that is displayed when a command does not exist.
        The logs parameter allows you to choose whether or not you want everything 
        displayed in the terminal to be rewritten in the logs. The animation and 
        cooldown parameters will define the display of CLI messages. Finally there is the
        help_cmd parameter which allows you to choose whether or not you want the CLI's 
        default help command.
        To launch the CLI you must use the run method of the CLI object.

        Exemple usage::

            >>> import PyCLI
            >>> cli = PyCLI.CLI(prompt="Python@CLI\\>", logs=True, animation=True, cooldown=15, help_cmd=True, not_exist="This command does not exist.\nDo help to get the list of existing commands.")
            >>> @cli.command()
            >>> def hello_world():
            >>>     print("Hello World")
            >>> cli.run()
        """
        self.__cmd = []
        self.prompt = prompt
        self.not_exist = not_exist
        self.logs = logs
        self.animation = animation
        self.cooldown = cooldown

        if platform.system() == "Windows": self.__clear_cmd = "cls"
        elif platform.system() in ["Linux", "Darwin"]: self.__clear_cmd = "reset"
        
        if help_cmd:
            @self.command(alias=["?"], doc=self.help.__doc__)
            def help() -> None:
                self.help()
        else: del self.help

        @self.command(alias=[self.__clear_cmd], name="clear-host", doc=self.clear_host.__doc__)
        def clear_host() -> None:
            self.clear_host()

        @self.command(alias=["exit"], doc=self.leave.__doc__)
        def leave() -> None:
            self.leave()

    def command(self,
                name: str = None,
                doc: str = None,
                alias : list = []
                ) -> callable:
        """
        The command decorator allows you to define a function as a command for the CLI. You 
        can enter the name and/or description in the name and doc parameters. If you
        don't, the command name will be the same name as the function. And for the description
        you can put it in doc form for your functions.

        Exemples usages::

            >>> import PyCLI
            >>> cli = PyCLI.CLI()
            >>> @cli.command(name="Hello World", doc="This command write hello world in the terminal.")
            >>> def display_hello_world():
            >>>     print("Hello World")
            >>> cli.run()

            >>> import PyCLI
            >>> cli = PyCLI.CLI()
            >>> @cli.command()
            >>> def hello_world():
                    "This command write hello world in the terminal."
            >>>     print("Hello World")
            >>> cli.run()
        """
        def decorator(func: callable) -> callable:
            def wrapper(name:str, 
                        doc: str, 
                        alias: list) -> None:
                name = name.replace(" ", "_").lower()

                types = []
                args = []
                for arg in inspect.signature(func).parameters.items():
                    types.append(str(arg[1].annotation).replace("<class '", "").replace("'>", ""))
                    args.append(f"[{arg[0]}]")
                exist = False
                for nmb, value in enumerate(self.__cmd):
                    for i in alias:
                        for j in value["alias"]:
                            if i == j:
                                raise AliasAlreadyUsing(f'[{value["name"]}] Alias "{i}" is already used.')
                    if value["name"] == name:
                        self.__cmd[nmb] = {
                            "name": name,
                            "doc": doc,
                            "function": func,
                            "args": args,
                            "types": types,
                            "alias": alias,
                        }
                        exist = True
                if not exist:
                    self.__cmd.append({
                        "name": name,
                        "doc": doc,
                        "function": func,
                        "args": args,
                        "types": types,
                        "alias": alias,
                    })
            return wrapper(name=name if name else func.__name__, 
                           doc=doc if doc else func.__doc__, 
                           alias=alias)
        return decorator
    
    def leave(self) -> None:
        "Close the terminal."
        os.kill(os.getpid(), 9)

    def clear_host(self) -> None:
        "Reset the display of the terminal."
        os.system(self.__clear_cmd)
    
    def help(self) -> None:
        "Displays info about terminal commands."
        text = ""
        for i in self.__cmd:
            doc = ""
            if i["doc"] is not None:
                doc += i["doc"]
            text += "Alias    "+ ", ".join(i["alias"])+" -> "+i["name"]+" "+" ".join(map(str, i["args"]))+doc+"\n"
        echo(text[:-1], animation=self.animation, cooldown=self.cooldown, logs=self.logs)

    def run(self) -> None:
        "This method of the CLI object allows you to launch the CLI after you have created all your commands."
        if self.logs: write_logs(*self.__cmd)
        while True:
            try:
                self.__cmd = sorted(self.__cmd, key=lambda x: x["name"])
                entry = prompt(self.prompt, animation=self.animation, cooldown=self.cooldown).lower()
                exist = False
                for i in self.__cmd:
                    if i["name"] == entry.split(" ")[0] or entry.split(" ")[0] in i["alias"]:
                        exist = True
                        args = []
                        for nmb, arg in enumerate(entry.split(" ")[1:len(i["args"])+1]):
                            for type in i["types"][nmb].split(" | "):
                                try:
                                    if i["types"][nmb] == "int": args.append(int(arg))
                                    elif i["types"][nmb] == "float": args.append(float(arg))
                                    elif i["types"][nmb] == "complex": args.append(complex(arg))
                                    elif i["types"][nmb] == "bool": args.append(bool(arg))
                                    elif i["types"][nmb] == "bytes": args.append(bytes(arg))
                                    elif i["types"][nmb] == "bytearray": args.append(bytearray(arg))
                                    else: args.append(arg)
                                    error = False
                                    break
                                except: continue
                            if error: raise ValueError(f"[{i[args][nmb]}] Could not convert string to {i['types'][nmb].replace('|', 'or')}.")
                        i["function"](*args)
                        break
                if not exist: echo(self.not_exist, animation=self.animation, cooldown=self.cooldown, logs=self.logs)
            except KeyboardInterrupt: continue
            except Exception as e:
                print(e)
                continue

def echo(*values: object,
         sep: str = " ",
         end: str = "\n",
         animation: bool = True,
         cooldown: float or int = 0.1,
         logs: bool = True
         ) -> None:
    """
    The echo method works like the print method which is already implemented in python but has a progressive 
    display system if the value of the animation parameter is set to True and also has a logging system that 
    writes the text you enter to the daily logs which is by default enabled. The cooldown parameter corresponds
    to the exposure time before displaying the next character (in MS) of the text you have entered if the 
    animation parameter is set to True.
    

    Exemple usage::

        >>> import PyCLI
        >>> PyCLI.echo("Hello World", animation=True, cooldown=15, logs=True, end="\n", sep=" ")
    """
    output = sep.join(map(str, values))
    for line in output.split("\n"):
        if animation:
            text = ""
            for i in line:
                text += i
                print(text, end="\r")
                time.sleep(cooldown / 1000)
        print(line, end=end)
    if logs:
        write_logs(output)


def prompt(__prompt: object = "",
           animation: bool = True,
           cooldown: float or int = 0.1,
           logs: bool = True
           ) -> str:
    """
    The prompt method works like the input method which is already implemented in python but has a progressive display 
    system if the value of the animation parameter is set to True and also includes a logging system that writes the 
    text that the user will respond to in the daily logs. The logging system is enabled by default. The cooldown 
    parameter corresponds to the exposure time before displaying the next character (in MS) of the text you have entered
    if the animation parameter is set to True.


    Exemple usage::

        >>> import PyCLI
        >>> PyCLI.prompt("What's your name ?", animation=True, cooldown=15, logs=True, end="\n", sep=" ")
    """
    for line in str(__prompt).split("\n"):
        if animation:
            text = ""
            for i in line:
                text += i
                print(text, end="\r")
                time.sleep(cooldown / 1000)
    returned = input(str(__prompt))
    if logs:
        write_logs(returned)
    return returned


def write_logs(*values: object,
               sep: str = " ",
               end: str = "\n",
               ) -> None:
    """
    The write_logs method allows to write in the daily logs. This method works like the print method which is already 
    implemented in python for the sep and end parameters.

    Exemple usage::

        >>> import PyCLI
        >>> PyCLI.write_logs("CLI was starting.")
    """
    text = sep.join(map(str, values)) + end
    if not os.path.exists("latest"):
        os.mkdir("latest")
    month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    time_now = f"{datetime.today().year}/{month[datetime.today().month - 1]}/{datetime.today().day} {datetime.today().hour}:{datetime.today().minute}:{datetime.today().second}"
    with open(f"latest/{datetime.today().date()}.log", "a", encoding="UTF-8") as file:
        file.write(f"[{time_now}] {text}")

class AliasAlreadyUsing(Exception):
    pass