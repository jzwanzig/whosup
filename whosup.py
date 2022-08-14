#!/usr/bin/env python

import tkinter as tk
from tkinter import font as tkFont
import json
import subprocess
import os
import yaml
import argparse

def get_args():
    parser=argparse.ArgumentParser()
    parser.add_argument("-f","--file",help="YAML file containing server and slack data")
    args=parser.parse_args()

    if args.file:
        filename=args.file
    else:
        filename='whosup.yaml'
    
    return filename

def set_servers(app_data):

    servers=[]
    for server in app_data['servers']:
        the_server={'server':server['server'],'port':server['port'],'enabled':tk.IntVar(value=0)}
        servers.append(the_server)

    return servers

def get_status(servers):

    # on windows, we presume you've installed the nmap package, which provides the ncat command
    if os.name == 'nt':
        nccmd = 'ncat.exe'
    else:
        nccmd = 'netcat' # in linux, this command is called netcat and is typically already present

    return_status=[]
    for server in servers:
        cmd=[nccmd,'-v','-z','-w 1',server['server'],server['port']]
        result=subprocess.run(cmd,text=True,capture_output=True)
        return_status.append(result.returncode)

    return return_status

# slack is awesome as a messenger service, once you have a slack channel you can add a webhook to it to allow
# access through http posts
def slackmessage(server_names):

    if len(server_names) > 0:
        msg=" unreachable servers: "
        for server in server_names:
            msg=msg+server+" "
    else:
        msg=" all watched servers up "

    slackhttp='https://hooks.slack.com/services/'+app_data['slackhook']
    cmd=['curl', '-X', 'POST', '-H', 'Content-type: application/json', \
            '--data', json.dumps({"text":msg}), slackhttp]
    result=subprocess.run(cmd,text=True,capture_output=True)

def isChecked(servers,server_widgets):

    status = get_status(servers)
    for iserver,server in enumerate(servers):
        if server['enabled'].get() == 0:
            server_widgets[iserver].config(bg='#F0F0F0')
        else:
            if status[iserver] == 0:
                server_widgets[iserver].config(bg='#98FB98')
            else:
                server_widgets[iserver].config(bg='#FF6347')

class Application(tk.Frame):

    def __init__(self,master=None):
        tk.Frame.__init__(self,master)
        self.grid()
        self.createWidgets()

    def createWidgets(self):
       
        self.servers=set_servers(app_data)
        self.server_widgets=[]
        for iserv,server in enumerate(self.servers):
            self.server_widgets.append(tk.Checkbutton(self,text=server['server'],variable=server['enabled'],font=helv12,command=lambda : isChecked(self.servers,self.server_widgets)))
            self.server_widgets[iserv].grid(column=0,row=iserv)
    
        self.QUIT=tk.Button(self,text="QUIT",font=helv12,command=root.destroy)
        self.QUIT.grid(column=0,row=len(self.servers)+1)

        self.server_down=False
        self.old_server_down=False
        
        self.onUpdate()

    def onUpdate(self):

        self.old_server_down = self.server_down
        self.unreachable_servers=[]
        self.server_status=get_status(self.servers)
        for iwidget,widget in enumerate(self.server_widgets):
            if self.servers[iwidget]['enabled'].get() == 1:
                if self.server_status[iwidget] == 0: 
                    widget.config(text=self.servers[iwidget]['server'],bg='#98FB98')
                else:
                    widget.config(text=self.servers[iwidget]['server'],bg='#FF6347')
                    self.unreachable_servers.append(self.servers[iwidget]['server'])

        self.short_interval = 60000 # 1 minute between checks
        self.long_interval = 900000 # 15 minutes between checks
        if len(self.unreachable_servers) > 0:
            self.server_down = True
            slackmessage(self.unreachable_servers)
            self.time_interval=self.short_interval
        else:
            self.server_down = False
            if self.old_server_down and not self.server_down:
                slackmessage(self.unreachable_servers)
            self.time_interval=self.long_interval

        self.after(self.time_interval,self.onUpdate)


filename=get_args()
with open(filename) as fp:
    app_data = yaml.load(fp,Loader=yaml.loader.BaseLoader)

root = tk.Tk()
root.title("Who\'s up")
helv12 = tkFont.Font(family='Helvetica', size=12, weight=tkFont.BOLD)
app = Application(master=root)
root.mainloop()

