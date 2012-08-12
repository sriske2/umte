#!/usr/bin/python3
# -*- coding:utf8 -*-
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

umte.py

umte, or "Uber Minimal Text Editor" is a python Gtk3 text editor built
with simplicity in mind.

"""

import os
import errno
import configparser
import time
from gi.repository import Gtk, GtkSource, Gdk
# The version of pyxdg in Fedora's repositories is out of date, so use a
# more recent version that supports python3
import xdg.BaseDirectory
import umtelibs

default_config = """[view]
linenumbers = no
"""


class Config(object):
    """
    The configuration class for umte to handle configuration stuff.

    __init__:
    Define the config file and path and check if they exist.

    check_for_conf_path:
    Check if the config path (~/.config/umte/) exists, create it if not.
    
    check_for_conf_file:
    Check if the config file (~/.config/umte/umte.conf) exists, create it if not.
    
    """
    
    def __init__(self, program_name):
        self.conf_file = os.path.join(xdg.BaseDirectory.xdg_config_home, 
                                        program_name, 
                                        program_name + ".conf")
        self.conf_path = os.path.join(xdg.BaseDirectory.xdg_config_home,
                                        program_name + '/')
        self.check_for_conf_path()
        self.check_for_conf_file()

        # Load the parser and read the conf file
        self.config = configparser.ConfigParser()
        self.config.read(self.conf_file)
        
    def check_for_conf_path(self):
        """Check for the conf_path, attempt to create if it doesn't exist"""
        if os.path.exists(self.conf_path):
            print("Config directory exists.")
        else:
            print("Config directory does not exists, creating")
            self.mkdir_p(self.conf_path)
            print("Config directory created")
    
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
    
    def mkdir_p(self, path):
        """mkdir -p functionality"""
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                pass
            else: raise


class umte(object):

    def __init__(self):
        # Some information about the program
        # This will be used in the about_dialog
        self.name = "umte"
        self.version  = "0.0.1"
        self.copyright_string = "Copyright 2012 Skyler Riske"
        self.comments = "comments"
        self.license = "GNU GPLv3"
        self.license_type = Gtk.License.GPL_3_0
        self.icon = Gtk.Image.new_from_file("icons/umte-128.png").get_pixbuf()

        self.path = None
        self.title = 'untitled - ' + self.name

        # Load the ui from the glade file
        self.builder = Gtk.Builder()
        self.builder.add_from_file("ui/umte.glade")
        
        # Connect the handlers to their callback functions.
        handler = {
            "on_window1_delete_event" : self.on_quit_item_activate,
            "on_new_file_item_activate" : self.on_new_file_activate,
            "on_open_item_activate" : self.on_open_item_activate,
            "on_save_item_activate" : self.on_save_item_activate,
            "on_save_as_item_activate" : self.on_save_as_item_activate,
            "on_close_file_item_activate" : self.on_close_file_item_activate,
            "on_quit_item_activate" : self.on_quit_item_activate,
            "on_undo_item_activate" : self.on_undo_item_activate,
            "on_redo_item_activate" : self.on_redo_item_activate,
            "on_cut_item_activate" : self.on_cut_item_activate,
            "on_copy_item_activate" : self.on_copy_item_activate,
            "on_paste_item_activate" : self.on_paste_item_activate,
            "on_delete_item_activate" : self.on_delete_item_activate,
            "on_select_all_item_activate" : self.on_select_all_item_activate,
            "on_insert_date_item_activate" : self.on_insert_date_item_activate,
            "on_change_case_item_activate" : self.on_change_case_item_activate,
            "on_find_rep_item_activate" : self.on_find_rep_item_activate,
            "on_linenumber_item_toggled" : self.on_linenumber_item_toggled,
            "on_about_item_activate" : self.on_about_item_activate
                }
        self.builder.connect_signals(handler)

        self.add_text_area()
        self.create_clipboard()

        # References widgets from the glade file for later usage.
        self.menubar = self.builder.get_object("menubar1")
        self.undo_item = self.builder.get_object("undo_item")
        self.redo_item = self.builder.get_object("redo_item")
        self.linenum_check = self.builder.get_object("linenumber_item")
        self.find_rep_box = self.builder.get_object("find_rep_box")
        self.find_entry = self.builder.get_object("find_entry")
        self.replace_entry = self.builder.get_object("replace_entry")
        self.statusbar = self.builder.get_object("statusbar1")

        # Load the statusbar manager
        self.status_manager = StatusbarManager(self.statusbar)
        self.status_manager.update_statusbar(self.buff)

        # load the language manager
        self.lang_manager = GtkSource.LanguageManager()

        # Load the config
        #self.config = Config(self.name)
        #self.check_config()

        # Show the window
        self.win = self.builder.get_object("window1")
        self.win.show_all()
        self.set_title(self.title)
        
        #self.menubar.hide()

    def add_text_area(self):
        """Add a GtkSource View to the window."""
        self.text_area = GtkSource.View()
        # Add the text area to a scrolled window
        self.scroll1 = Gtk.ScrolledWindow()
        self.scroll1.add(self.text_area)
        self.buff = GtkSource.Buffer()
        self.buff.connect('changed', self.on_text_changed)
        self.text_area.set_buffer(self.buff)
        # Add the text area to the box from the glade file
        self.main_box = self.builder.get_object("main_box")
        self.main_box.pack_start(self.scroll1, True, True, 0)
        
        # Reposition self.scroll1 so it's above the statusbar.
        self.main_box.reorder_child(self.scroll1, 1)
    
    def create_clipboard(self):
        """Create a clipboard object"""
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    def save_as_file(self):
        """Prompt the user with a save dialog and write the file."""
        save_dialog = Gtk.FileChooserDialog(
            "Save As", self.win, 
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

        # Make sure the user is warned if they're overwriting an existing file.
        save_dialog.set_do_overwrite_confirmation(True)
        # Suggest a generic filename.
        save_dialog.set_current_name("untitled.txt")

        response = save_dialog.run()
        if response == Gtk.ResponseType.OK:
            # Get the path and filename then save the file.
            self.path = save_dialog.get_filename()
            self.filename = os.path.basename(self.path)
            self.write_file(self.path)
        
            # Add the filename to the window's title
            self.title = self.filename + " - " + self.name
            self.set_title(self.title)

        elif response == Gtk.ResponseType.CANCEL:
            pass

        save_dialog.destroy()
    
    def write_file(self, file_path):
        try:
            _file = open(file_path, 'w', encoding='utf-8')
        except IOError:
            self.error("Unable to open " + file_path, "check that you have proper permissions")
            return
        
        # Get the text from the buffer and add a \n to it
        start, end = self.buff.get_bounds()
        text = self.buff.get_text(start, end, False) + "\n"
        # Write to the file and close it
        _file.write(text)
        _file.close()
        # 
        self.buff.set_modified(False)

        # Remove the modification status from the title since the file has been saved.
        self.title = self.filename + ' - ' + self.name
        self.set_title(self.title)
    
    def set_title(self, title):
        """Set the title of the window to title."""
        self.win.set_title(title)
    
    def close_file(self):
        """
        Clear the buffer, reset the title, and reset the 
        buffer's modification status.
        """
        self.buff.set_text("")
        self.buff.set_modified(False)
        self.title = 'untitled - ' + self.name
        self.set_title(self.title)
    
    def on_text_changed(self, widget, data=None):
        """This will check for a few things everytime the buffer is modified."""
        """if self.buff.can_undo() is False:
            self.undo_item.set_sensitive(False)
        else:
            self.undo_item.set_sensitive(True)

        if self.buff.can_redo() is False:
            self.redo_item.set_sensitive(False)
        else:
            self.redo_item.set_sensitive(True)
        """
        # Print the position of the cursor
        #print(self.buff.get_property('cursor-position'))
        self.undo_item.set_sensitive(True)

        if self.buff.get_modified() is True:
            if self.title[0] != '*':
                self.title = '*' + self.title
                self.set_title(self.title)

        # Update the statusbar with the latest information
        self.status_manager.update_statusbar(self.buff)
    
    def open_file(self):
        """Open a file from disk"""
        open_dialog = Gtk.FileChooserDialog("Open",
                            self.win,
                            Gtk.FileChooserAction.OPEN,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                            Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        
        response = open_dialog.run()
        if response == Gtk.ResponseType.OK:
            # If the user pressed OK
            # Get the path and filename
            self.path = open_dialog.get_filename()
            self.filename = os.path.basename(self.path)

            # Add the filename to the window's title
            self.title = self.filename + " - " + self.name
            self.set_title(self.title)

            # Add the contents of the file to the buffer
            _file = open(self.path, 'r', encoding='utf-8')
            self.buff.begin_not_undoable_action()
            self.buff.set_text(_file.read())
            self.buff.end_not_undoable_action()
            _file.close()

            ### syntax highlighting ###
            # Figure out what kind of syntax we need to highlight
            language =  self.lang_manager.guess_language(self.path, None) 
            self.buff.set_language(language)
            print(self.lang_manager.get_language_ids())

            self.buff.set_modified(False)
            open_dialog.destroy()


        elif response == Gtk.ResponseType.CANCEL:
            # The user clicked CANCEL
            open_dialog.destroy()

    def new_file(self):
        """Close the currently open file and start a new file"""
        # In this program, creating a new file is the same as closing the
        # current one, so just run the self.close_file() function
        self.close_file()
    
    """def check_for_save(self):

        Check if the buffer has been modified and prompt the user to save
        if it has been modified.

        ret = False
        
        if self.buff.get_modified():
            dialog = Gtk.MessageDialog(self.win,
                    Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.QUESTION,
                    Gtk.ButtonsType.NONE,
                    "There are unsaved changes.")
            dialog.format_secondary_text("Before you close this file, do you want to save changes?")
            # Add some buttons
            dialog.add_buttons("Close without saving", 41)
            dialog.add_buttons(Gtk.STOCK_CANCEL, 42)
            dialog.add_buttons(Gtk.STOCK_SAVE, 43)

            response = dialog.run()
            if response == 41:
                ret = False
            elif response == 42:
                ret = "cancel"
            elif response == 43:
                ret = True

            dialog.destroy()

        else:
            return("not_modified")

        return(ret)"""

    def show_about_dialog(self):
        """Create and show an about dialog"""
        ab_dialog = Gtk.AboutDialog()
        ab_dialog.set_program_name(self.name)
        ab_dialog.set_version(self.version)
        ab_dialog.set_copyright(self.copyright_string)
        ab_dialog.set_comments(self.comments)
        ab_dialog.set_license_type(self.license_type)
        ab_dialog.set_logo(self.icon)

        ab_dialog.run()
        ab_dialog.destroy()

    def error(self, message, secondary_message):
        """
        Show an error dialog and print to the terminal with message 
        and secondary_message.

        This will be used whenever something does not go as it should
        and the user needs to be notified of it.

        """
        print("ERROR: " + message + ' -- ' + secondary_message)

        error_dialog = Gtk.MessageDialog(self.win,
                Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                message)
        error_dialog.format_secondary_text(secondary_message)
        error_dialog.run()
        error_dialog.destroy()

    def change_case(self, text):
        """
        Take the selection (text) and cycle it through different cases.

        Similar to the extremely useful feature in Microsoft Word, 
        take text, which will be the user's selected text and cycle it 
        through being uppercase, lowercase and title format each time
        the user runs this function and return the result.
        """
        if text.istitle():
            newtext = text.upper()

        elif text.isupper():
            newtext = text.lower()

        elif text.islower():
            newtext = text.title()

        return(newtext)

    
    def check_config(self):
        """Read the config's values and customize the program to what it specifies."""
        # Line numbers
        if self.config.read_config("view", "linenumbers") == 'yes':
            # If the config says linenumbers should be shown
            pass

    
    # callback methods
    def on_new_file_activate(self, widget, data=None):
        if self.buff.get_modified() == True:
            # If the buffer has been modified
            dialog = Gtk.MessageDialog(self.win,
                    Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.WARNING,
                    Gtk.ButtonsType.NONE,
                    "There are unsaved changes.")
            dialog.format_secondary_text("Before you open a new file, do you want to save changes?")
            # Add some buttons
            dialog.add_buttons(Gtk.STOCK_CANCEL, 42)
            dialog.add_buttons(Gtk.STOCK_SAVE, 43)

            response = dialog.run()
            if response == 42:
                pass
            elif response == 43:
                self.on_save_item_activate(None)
                self.new_file()

            dialog.destroy()
        else:
            # If the buffer hasn't been modified, just run the new_file() function.
            self.new_file()

    def on_open_item_activate(self, widget, data=None):
        self.open_file()
    
    def on_save_item_activate(self, widget, data=None):
        """
        if the current file is unsaved, run the save_as function, 
        otherwise just write the file.
        """
        if self.path != None:
            self.write_file(self.path)
        else:
            self.save_as_file()
    
    def on_save_as_item_activate(self, widget, data=None):
        self.save_as_file()
    
    def on_close_file_item_activate(self, widget, data=None):
        """
        Close the current file, but prompt the user for save if the buffer has
        been modified.
        """
        if self.buff.get_modified() == True:
            # If the buffer has been modified
            dialog = Gtk.MessageDialog(self.win,
                    Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.WARNING,
                    Gtk.ButtonsType.NONE,
                    "There are unsaved changes.")
            dialog.format_secondary_text("Before you close this file, do you want to save changes?")
            # Add some buttons
            dialog.add_buttons("Close without saving", 41)
            dialog.add_buttons(Gtk.STOCK_CANCEL, 42)
            dialog.add_buttons(Gtk.STOCK_SAVE, 43)

            response = dialog.run()
            if response == 41:
                self.close_file()
            elif response == 42:
                pass
            elif response == 43:
                self.on_save_item_activate(None)
                self.close_file()

            dialog.destroy()
        else:
            # If the buffer hasn't been modified, just close the file.
            self.close_file()

    
    def on_quit_item_activate(self, widget, data=None):
        """Stop the Gtk loop when activated."""
        Gtk.main_quit()
    
    def on_undo_item_activate(self, widget, data=None):
        """Undo the last action when activated"""
        self.buff.undo()
    
    def on_redo_item_activate(self, widget, data=None):
        """Redo the last action when activated."""
        self.buff.redo()

    def on_cut_item_activate(self, widget, data=None):
        """Cut the selection to the clipboard when activated."""
        self.buff.cut_clipboard(self.clipboard, True)

    def on_copy_item_activate(self, widget, data=None):
        """Copy selection to the clipboard when activated."""
        self.buff.copy_clipboard(self.clipboard)
    
    def on_paste_item_activate(self, widget, data=None):
        """paste the clipboard to the buffer when activated."""
        self.buff.paste_clipboard(self.clipboard, None, True)
    
    def on_delete_item_activate(self, widget, data=None):
        """Delete the current selection when activated."""
        self.buff.delete_selection(True, True)
    
    def on_select_all_item_activate(self, widget, data=None):
        """Select all text when activated."""
        start, end = self.buff.get_bounds()
        self.buff.select_range(start, end)
    
    def on_find_rep_item_activate(self, widget, data=None):
        """Toggle the find and replace box."""
        if self.find_rep_box.get_visible() is False:
            self.find_rep_box.set_visible(True)
            # Give focus to the find_entry when shown
            self.find_entry.set_can_focus(True)
            self.find_entry.grab_focus()
        elif self.find_rep_box.get_visible() is True:
            self.find_rep_box.set_visible(False)
            # Give focus to the text area when the find menu is hidden
            self.text_area.grab_focus()

    def on_insert_date_item_activate(self, widget, data=None):
        """Insert the current date in locale format at cursor position into the buffer."""
        date = time.strftime('%x')
        self.buff.insert_at_cursor(date, len(date))

    def on_change_case_item_activate(self, widget, data=None):
        #FIXME find a way to replace the selection with the new text.
        start, end = self.buff.get_selection_bounds()
        selection = self.buff.get_text(start, end, False)
        print(selection)
        
       # # Delete the selection and replace it with the new text
        #self.buff.delete_selection(True, True)
        self.buff.insert(start, self.change_case(selection), -1)

    def on_linenumber_item_toggled(self, widget, data=None):
        if widget.get_active():
            self.text_area.set_show_line_numbers(True)
            # Write this change to the config
            self.config.write_config("view", "linenumbers", "yes")
        else:
            self.text_area.set_show_line_numbers(False)
            # Write this change to the config
            self.config.write_config("view", "linenumbers", "no")
    
    def on_about_item_activate(self, widget, data=None):
        self.show_about_dialog()
    

class StatusbarManager(object):
    """
    A statusbar manager for umte to show useful information.

    """
    #TODO statusbar info idea: line: 44, column: 22, Spaces: 4

    def __init__(self, statusbar):
        self.statusbar = statusbar
        self.stat_id = self.statusbar.get_context_id("status_id")

    def create_status_string(self):
        self.status_string = " lines: {}  length: {}"\
            .format(self.line_count, self.char_count)

    def update_statusbar(self, buff):
        self.clear_statusbar()
        self.get_line_amount(buff)
        self.get_char_amount(buff)
        
        # Update the status string to the latest information
        self.create_status_string()
        # Push it to the statusbar
        self.statusbar.push(self.stat_id, self.status_string)
    
    def clear_statusbar(self):
        """Clear the statusbar of all messages"""
        self.statusbar.remove_all(self.stat_id)

    def get_line_amount(self, buff):
        self.line_count = buff.get_line_count()

    def get_char_amount(self, buff):
        """Get the amount of characters in the buffer"""
        self.char_count = buff.get_char_count()

umte = umte()
Gtk.main()
