#!/usr/bin/python
# -*- coding:utf8 -*-
#
# This program is licensed under the MIT License (MIT),
# see LICENSE for details.
#TODO add a menu item to open the current file's directory
"""
umte.py

umte, or "Uber Minimal Text Editor" is a python Gtk3 text editor built
with simplicity in mind.
umte is designed to be a primarily keyboard-shortcut based text editor to
maximise efficiency.
"""

from gi.repository import Gtk, GtkSource, Gdk
import os
import errno
import ConfigParser as configparser
import xdg.BaseDirectory

default_config = """[view]
linenumbers = no
"""

class Config:
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
            _file = open(self.conf_file, 'w')
            _file.write(default_config)
            _file.close()
            print("config file has been created")
    
    def read_config(self, section, _property):
        """Read the _property's value in section and return the value."""
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
        _file = open(self.conf_file, 'w')
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

class umte:
    def __init__(self):
        self.name = "umte"
        self.path = None
        self.title = 'untitled - ' + self.name

        # Load the ui from the glade file
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../ui/umte-filemenu.glade")
        
        # Connect the handlers to their callback functions.
        handler = {
            "on_window1_delete_event" : self.on_quit_item_activate,
            "on_find_entry_activate" : self.on_find_entry_activate,
            "on_find_entry_changed" : self.on_find_entry_changed,
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
            "on_find_rep_item_activate" : self.on_find_rep_item_activate,
            "on_linenumber_item_toggled" : self.on_linenumber_item_toggled,
            "on_about_item_activate" : self.on_about_item_activate,
            "on_find_entry_activate" : self.on_find_entry_activate,
            "on_find_entry_changed" : self.on_find_entry_changed,
            "on_replace_entry_activate" : self.on_replace_entry_activate,
            "on_replace_entry_changed" : self.on_replace_entry_changed,
            "on_find_rep_close_button_clicked" : self.on_find_rep_close_button_clicked
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

        # Load the config
        self.config = Config(self.name)
        self.check_config()

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
    
    def create_clipboard(self):
        """Create a clipboard object"""
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    def save_as_file(self):
        """Prompt the user with a save dialog and write the file."""
        save_dialog = Gtk.FileChooserDialog("Save As", self.win, 
                                Gtk.FileChooserAction.SAVE,
                                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        # Tell the user if they're overwriting an existing file.
        save_dialog.set_do_overwrite_confirmation(True)
        # Give a default filename
        save_dialog.set_current_name("untitled.txt")

        response = save_dialog.run()
        if response == Gtk.ResponseType.OK:
            # Get the path and filename then save the file.
            self.path = save_dialog.get_filename()
            self.filename = os.path.basename(self.path)
            self.write_file(self.path)
        
            # Add the filename to the window's title
            self.title = self.filename + " - " + self.name + ' - ' + str(os.path.getsize(self.path))
            self.set_title(self.title)

        elif response == Gtk.ResponseType.CANCEL:
            pass

        save_dialog.destroy()
    
    def write_file(self, file_path):
        try:
            _file = open(file_path, 'w')
        except IOError:
            print("Unable to open " + file_path)
        
        # Get the text from the buffer and add a \n to it
        start, end = self.buff.get_bounds()
        text = self.buff.get_text(start, end, False) + "\n"
        # Write to the file and close it
        _file.write(text)
        _file.close()
        # 
        self.buff.set_modified(False)

        # Remove the modification status from the title since the file has been saved.
        self.title = self.filename + ' - ' + self.name + ' - ' + str(os.path.getsize(file_path))
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
        if self.buff.get_modified() is True:
            if self.title[0] != '*':
                self.title = '*' + self.title
                self.set_title(self.title)
    
    def open_file(self):
        pass
    
    def check_for_save(self):
        """
        Check if the buffer has been modified and prompt the user to save
        if it has been modified.
        """
        ret = False
        
        if self.buff.get_modified():
            dialog = Gtk.MessageDialog(self.win,
                    Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.QUESTION,
                    Gtk.ButtonsType.YES_NO,
                    "Do you want to save your changes?")
            response = dialog.run()
            if response == Gtk.ResponseType.NO:
                ret = False
            else:
                ret = True
        return(ret)
    
    def check_config(self):
        """Read the config's values and customize the program to what it specifies."""
        # Line numbers
        if self.config.read_config("view", "linenumbers") == 'yes':
            self.text_area.set_show_line_numbers(True)
            # Check off the line number item in the menu.
            self.linenum_check.set_active(True)
        else:
            self.text_area.set_show_line_numbers(False)
    
    # callback functions
    def on_find_entry_activate(self, widget, data=None):
        print("Find entry activated!")
    
    def on_find_entry_changed(self, widget, data=None):
        print("Text changed in find entry!")

    def on_new_file_activate(self, widget, data=None):
        print("new file item activated!")

    def on_open_item_activate(self, widget, data=None):
        pass
    
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
    
    def on_linenumber_item_toggled(self, widget, data=None):
        if widget.get_active() and self.confi.read_config("view", "linenumbers") is not True:
            self.text_area.set_show_line_numbers(True)
            # Write this change to the config
            self.config.write_config("view", "linenumbers", "yes")
        else:
            self.text_area.set_show_line_numbers(False)
            # Write this change to the config
            self.config.write_config("view", "linenumbers", "no")
    
    def on_about_item_activate(self, widget, data=None):
        print("About item activated!")
        about_dialog = self.builder.get_object("umte_aboutdialog")
        about_dialog.show()
        about_dialog.run()
        about_dialog.destroy()
        #TODO delete the about dialog from glade, make it by hand
    
    # Find menu callbacks
    def on_find_entry_activate(self, widget, data=None):
        pass

    def on_find_entry_changed(self, widget, data=None):
        pass

    def on_replace_entry_activate(self, widget, data=None):
        pass
    
    def on_replace_entry_changed(self, widget, data=None):
        if widget.get_text() != "":
            pass
    
    def on_find_rep_close_button_clicked(self, widget, data=None):
        self.on_find_rep_item_activate(None)

umte = umte()
Gtk.main()
