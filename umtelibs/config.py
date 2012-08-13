"""
Copyright (C) 2012 Skyler Riske

This program is licensed under the GNU GPLv3, see LICENSE for details.
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Author(s): Skyler Riske

umtelibs/config.py

Nearly everything related to configuration with umte is contained in here.

config files will be stored in the user's ~/.config/ directory
inside of the umte folder that will be created.
"""

import os
# The version of pyxdg in Fedora's repositories is out of date, so use a
# more recent version that supports python3
import xdg.BaseDirectory

default_config = """[view]
linenumbers = no
"""


class Config(object):
    """
    The configuration class for umte to handle configuration stuff.

    __init__:
    Define the config file and path and check if they exist.

    check_for_conf_file:
    Check if the config file (~/.config/umte/umte.conf) exists, create it if not.
    
    """
    
    def __init__(self, program_name):
        self.conf_file = os.path.join(xdg.BaseDirectory.xdg_config_home, 
                                        program_name, 
                                        program_name + ".conf")
        # Ensure the directory exists, create it if not, and get the path of it
        # Config path: ~/.config/umte/
        self.conf_path = xdg.BaseDirectory.save_config_path(program_name)

        self.check_for_conf_file()

        # Load the parser and read the conf file
        self.config = configparser.ConfigParser()
        self.config.read(self.conf_file)
        
    def check_for_conf_file(self):
        """Check if the conf_file exists, create a default conf_file if one doesn't exist"""
        if os.path.exists(self.conf_file):
            print("config file exists.")
        else:
            print("config file does not exist, creating default config file.")
            try:
                _file = open(self.conf_file, 'w', encoding='utf-8')
                _file.write(default_config)
                _file.close()
                print("config file has been created")

            except:
                print("Unable to create config file, using default config")
    
    def read_config(self, section, _property):
        """Read the _property's value in section and return it."""
        return(self.config.get(section, _property))
        print("Reading config")

    def write_config(self, section, _property, value):
        """
        Set _property's value to "value" in section and write changes 
        to the conf file.
        """
        #TODO Check for the conf_file and prompt a dialog if it doesn't exist
        # to ask if they want to create a default config.
        self.config.set(section, _property, value)
        # Write the changes to the conf_file
        _file = open(self.conf_file, 'w', encoding='utf-8')
        self.config.write(_file)
        _file.close()
        print("Successfully wrote changes to config")

    def reload_config(self):
        """Tell the parser to read the conf_file again."""
        self.config.read(self.conf_file)
