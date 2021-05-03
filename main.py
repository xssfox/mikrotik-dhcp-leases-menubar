import rumps
import routeros_api
import appdirs
from appdirs import *
import tkinter as tk
import clipboard
import AppKit
from pytimeparse.timeparse import timeparse

from pypref import Preferences
pref = Preferences(filename="dhcpstatus.py", directory=user_data_dir("dhcpstatus", "xssfox"))
#pref.set_preferences({})


def configure(event=None):
    showMacDockIcon()
    global entryHostname, entryUsername, entryPassword, window
    window.deiconify()

    window.mainloop()

def closeRootWindow():
    global window
    window.withdraw()
    
def updateConfig(event):
    global config, window
    config = { 
        "hostname": entryHostname.get(),
        "username": entryUsername.get(),
        "password": entryPassword.get()
    }
    pref.set_preferences(config)
    window.withdraw()
    hideMacDockIcon()



def connect():
    global connection, api
    try:
        connection = routeros_api.RouterOsApiPool(config['hostname'], username=config['username'], password=config['password'], plaintext_login=True)
        api = connection.get_api()
    except:
        pass


def update_leases(sender=None):
    global api
    global menubar
    if not api:
        connect()
    if api:
        try:
            leases = api.get_resource('/ip/dhcp-server/lease').get()
            simple_leases = []
            for lease in leases:
                if lease['status'] == 'bound':
                    simple_leases.append({
                    "address": lease['address'],
                    "hostname": lease['host-name'] if 'host-name' in lease else "",
                    "lastseen": lease['last-seen'],
                    "lastseen_s": timeparse(lease['last-seen'])
                    })
            sorted_list = sorted(simple_leases, key=lambda k: k['lastseen_s']) 
            menu_items = [
                rumps.MenuItem(f"{x['address']} - {x['hostname']}", callback=action)
                for x in sorted_list
            ]
            menubar.menu.clear()
            menubar.menu = default_menus() + menu_items
        except:
            menubar.menu.clear()
            menubar.menu = default_menus()
    else:
        menubar.menu.clear()
        menubar.menu = default_menus()

    
class DhcpStatusBarApp(rumps.App):
    pass


def action(event):
    ip_address = event.title.split(" ")[0]
    clipboard.copy(ip_address.encode("utf-8"))

def hideMacDockIcon():
    # https://developer.apple.com/library/mac/#documentation/AppKit/Reference/NSRunningApplication_Class/Reference/Reference.html
    NSApplicationActivationPolicyProhibited = 2
    AppKit.NSApp.setActivationPolicy_(NSApplicationActivationPolicyProhibited)
def showMacDockIcon():
    # https://developer.apple.com/library/mac/#documentation/AppKit/Reference/NSRunningApplication_Class/Reference/Reference.html
    NSApplicationActivationPolicyRegular = 0
    AppKit.NSApp.setActivationPolicy_(NSApplicationActivationPolicyRegular)

def exit(event):
    rumps.quit_application()
def default_menus():
    return [rumps.MenuItem("Configure", callback=configure),rumps.MenuItem("Exit", callback=exit),rumps.MenuItem("----")]
if __name__ == "__main__":
    

    window = tk.Tk()
    
    window.withdraw()
    
    window.protocol("WM_DELETE_WINDOW", closeRootWindow)
    lblHostname = tk.Label(text="Hostname:")
    entryHostname = tk.Entry()
    lblUsername = tk.Label(text="Username:")
    entryUsername = tk.Entry()
    lblPassword = tk.Label(text="Password:")
    entryPassword = tk.Entry(show="*")
    # load default config
    try:
        
        config = {
            "hostname": pref.get("hostname"),
            "username": pref.get("username"),
            "password": pref.get("password")
        }
        
        entryHostname.insert(0, config['hostname'])
        entryUsername.insert(0, config['username'])
        entryPassword.insert(0, config['password'])

    except:
        pass
    
    connection = None
    api = None

    connect()
    
    save = tk.Button(text="Save")
    
    lblHostname.pack()
    entryHostname.pack()
    lblUsername.pack()
    entryUsername.pack()
    lblPassword.pack()
    entryPassword.pack()
    save.pack()
    save.bind('<Button-1>', updateConfig)

    
    hideMacDockIcon()
    
    menubar = DhcpStatusBarApp("📶")
    
    menubar.menu = default_menus()
    
    update_leases()
    
    timer = rumps.Timer(update_leases, 5)
    timer.start()
    
    menubar.run()
    