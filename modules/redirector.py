import cmd2
from cmd2.ansi import Fg
import os
import argparse
from prettytable import PrettyTable
from prettytable import MSWORD_FRIENDLY
import random
import string
import json

module = {}
campaign_list = []
modules_ids = []

class main(list):
    """Main function to initialize variables and calls the cmd2 package for the c2 module """
    def __init__(self,mod,campaign,project_id):
        global campaign_list
        global module

        if mod is not None:    
            module = mod
        
        campaign_list = campaign
        
        # Call cmd_main class 
        i = cmd_main()
        i.prompt = "(" + cmd2.ansi.style("Overlord", fg=Fg.RED, bg=None,bold=True, underline=False) + " : " + cmd2.ansi.style( project_id, fg=Fg.DARK_GRAY, bg=None,bold=True, underline=False) + cmd2.ansi.style("/redirector", fg=Fg.BLUE, bg=None,bold=True, underline=False) +")" +"$> "
        i.cmdloop()

def hide_cmd2_modules(self):
    # Remove most of the functionalities of the cmd2 package
    self.hidden_commands.append('py')
    self.hidden_commands.append('alias')
    self.hidden_commands.append('macro')
    self.hidden_commands.append('script')
    self.hidden_commands.append('shortcuts')
    self.hidden_commands.append('pyscript')
    self.hidden_commands.append('run_pyscript') 
    self.hidden_commands.append('edit')
    self.hidden_commands.append('run_script')
    self.hidden_commands.append('quit')
    self.hidden_commands.append('load')

class cmd_main(cmd2.Cmd):
    """cmd2 instance for c2 module"""
    # The mod dictionary for the c2 module
    mod ={}

    available_regions_list = []
    type_list = ["http","dns"]
    providers_list = []

    def __init__(self):
        super().__init__()
        # Hide the Quit funcitionality
        hide_cmd2_modules(self)
        global module
        global campaign_list
        global modules_ids

        dir_path = "config"
        if  os.path.exists(dir_path+"/config.json"):
            with open(dir_path+'/config.json', 'r') as filehandle:
                config = json.load(filehandle) 
                self.mod = config["mod_redirector"]
                self.providers_list = config["providers_list"]
                self.module_provider_parser.choices = self.providers_list

                for prov in self.providers_list:
                    if self.mod["provider"] == prov:
                        self.available_regions_list = config[prov]["regions"]
                        self.module_regions_parser.choices = self.available_regions_list
                        self.size_list = config[prov]["size"]
                        self.module_size_parser.choices = self.size_list
        else:
            print("The config/config.json file does not exists! Exiting...")
            return True             

        if module:
            self.mod = dict(module)
        else:
            self.mod["id"] = randomString()

        # Create list with modules id
        for c in campaign_list:
            if c["module"] != "dns_record" and c["module"] != "letsencrypt" and c["module"] != "mail" and c["module"] != "godaddy":
                modules_ids.insert(len(modules_ids),(c["id"]+"/"+c["module"]))
        
        #Starting creating localhost redirection
        modules_ids.insert(len(modules_ids),"localhost")
        self.mod_parser_redirectors.choices = modules_ids

    def do_back(self, arg):
        """Return to main menu"""
        return True

    def do_clear(self, arg):
        """Clears screen"""
        os.system('clear')

    def do_info(self,mod):
        """Prints variable table"""
        if mod :
            x = PrettyTable()
            x.title = mod["module"] + "/" +mod["id"]
            x.field_names = ["VARIABLE", "VALUE", "REQUIRED", "DESCRITPION"]
            x.add_row(["id", mod["id"], "N/A", "Module ID"])
            x.add_row(["type", mod["type"], "yes", "Type of traffic to redirect values are: HTTP/DNS."])
            x.add_row(["redirector_id",mod["redirector_id"] , "yes", "ID of the redirector to set up."])
            x.add_row(["provider", mod["provider"], "yes", "Provider to be used "])
            x.add_row(["region",mod["region"] , "yes", "Regions to create Droplet in."])
            x.add_row(["size",mod["size"] , "yes", "Droplet size to launch."])
            x.align["DESCRITPION"] = "l"
        else:
            x = PrettyTable()
            x.title = 'Redirector module'
            x.field_names = ["VARIABLE", "VALUE", "REQUIRED", "DESCRITPION"]
            x.add_row(["id", self.mod["id"], "N/A", "Module ID"])
            x.add_row(["type", self.mod["type"], "yes", "Type of traffic to redirect values are: HTTP/DNS."])
            x.add_row(["redirector_id",self.mod["redirector_id"] , "yes", "ID of the redirector to set up."])
            x.add_row(["provider", self.mod["provider"], "yes", "Provider to be used "])
            x.add_row(["region",self.mod["region"] , "yes", "Regions to create Droplet in."])
            x.add_row(["size",self.mod["size"] , "yes", "Droplet size to launch."])
            x.align["DESCRITPION"] = "l"
        print(x)

    # set command
    # create the top-level parser for the set command
    set_parser = argparse.ArgumentParser(prog='set')
    set_subparsers = set_parser.add_subparsers(title='set-commands', help='Sets the variables of the module')

    # create the parser for the "region" sub-command
    parser_region = set_subparsers.add_parser('region', help='Regions to create Droplet in. Defaults to LON1. Accepted values are NYC1/2/3, SFO1/2, AMS1/2, SGP1, LON1, FRA1, TOR1, BLR1.')
    module_regions_parser = parser_region.add_argument('region',choices=available_regions_list, type=str, help='example : [ set region <AMS1> ]')

    # create the parser for the "type" sub-command
    parser_type = set_subparsers.add_parser('type', help='Type of c2 Accepted values are: HTTP/DNS.')
    parser_type.add_argument('type' ,choices=type_list, type=str, help='example:  set type <http> ]')

    # create the parser for the "provider" sub-command
    parser_provider = set_subparsers.add_parser('provider', help='Provider to be used ')
    module_provider_parser = parser_provider.add_argument('provider',choices=providers_list, type=str, help='example: [ set provider <digitalocean> ]')

    # create the parser for the "redirector" sub-command
    parser_redirectors = set_subparsers.add_parser('redirector_id', help='ID of the redirector to set up.')
    mod_parser_redirectors = parser_redirectors.add_argument('redirector_id', type=str, help='example: [ set redirector_id <id>')

    # create the parser for the "size" sub-command
    parser_size = set_subparsers.add_parser('size', help='Size of the droplet.')
    module_size_parser = parser_size.add_argument('size', type=str, help='example: [ set size <s-1vcpu-1gb>] ')

    def set_region(self, arg):
        """Sets the region variable"""
        self.mod["region"]= arg.region
        # Change provider for all modules on AWS
        if self.mod["provider"] == "aws":
            notification = cmd2.ansi.style("***", fg=Fg.RED, bg=None,bold=True, underline=False)
            print(f"""\n{notification} Only one region is supported per project on AWS. {notification}\n""")
            global campaign_list
            for c in campaign_list:
                if c["provider"] == "aws":
                    if c["region"] != arg.region:
                        print(cmd2.ansi.style(f"""Module with {c["id"]} has region set to {c["region"]}. Replacing...""", fg=Fg.RED, bg=None,bold=True, underline=False))
                        c["region"] = arg.region

    def set_size(self, arg):
        """Sets the size variable"""
        self.mod["size"]= arg.size
    def set_redirector(self, arg):
        """Sets the redirector variable"""
        self.mod["redirector_id"] = arg.redirector_id

    def set_type(self, arg):
        """Sets the type variable"""
        self.mod["type"] = arg.type

    def set_provider(self, arg):
        """Sets the provider variable"""
        self.mod["provider"]= arg.provider

        dir_path = "config"
        if  os.path.exists(dir_path+"/config.json"):
            with open(dir_path+'/config.json', 'r') as filehandle:
                config = json.load(filehandle) 

                for prov in self.providers_list:
                    if self.mod["provider"] == prov:
                        self.available_regions_list = config[prov]["regions"]
                        self.module_regions_parser.choices = self.available_regions_list
                        self.size_list = config[prov]["size"]
                        self.module_size_parser.choices = self.size_list
                        self.mod["region"] = config[prov]["default_region"]
                        self.mod["size"] = config[prov]["default_size"]

    #Set handler functions for the sub-commands
    parser_size.set_defaults(func=set_size)
    parser_region.set_defaults(func=set_region)
    parser_type.set_defaults(func=set_type)
    parser_redirectors.set_defaults(func=set_redirector)
    parser_provider.set_defaults(func=set_provider)

    @cmd2.with_argparser(set_parser)
    def do_set(self, args):
        """Set the variables for the module"""
        func = getattr(args, 'func', None)
        if func is not None:
            # Call whatever sub-command function was selected
            func(self, args)
        else:
            # No sub-command was provided, so call help
            self.do_help('help')

    def do_add(self,args):
        """Adds c2 module to the project """
        global  module
        if self.mod["redirector_id"]:
            module = self.mod
            return True         
        else:
            print("The variable redirector_id can not be None!")

    # Command categories
    CMD_CAT_GENERAL = 'General'
    CMD_CAT_MODULE  = 'Module'

    cmd2.categorize((do_add,do_set), CMD_CAT_MODULE)
    cmd2.categorize(do_info, CMD_CAT_GENERAL)
    
#Create a random String
def randomString(stringLength=6):
    """Generate a random string of fixed length """
    letters = string.ascii_uppercase
    return ''.join(random.choice(letters) for i in range(stringLength))
