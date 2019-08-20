#!/usr/bin/python

from httplib2 import Http
from json import dumps
import json
import sys
import datetime
import configparser

#
# Google Chat API
# Scripting Zabbix Notifications in Google Chat Groups
#
# Dependencias:
#   pip install httplib2
#   pip install configparser
#

class ChatSender:

    INI_FILE = '/usr/share/zabbix/alertscripts/zabbix-google-chat/google_chat.ini'

    PROBLEM_IMG = 'https://png.pngtree.com/svg/20161208/status_warning_336325.png'
    ACK_IMG = 'https://static1.squarespace.com/static/549db876e4b05ce481ee4649/t/54a47a31e4b0375c08400709/1472574912591/form-3.png'
    RESOLVED_IMG = 'https://image.flaticon.com/icons/png/128/291/291201.png'

    def __init__(self, webhook_name):
        cp = configparser.RawConfigParser()
        try:
            cp.read(self.INI_FILE)
            if cp.has_section('zabbix'):
                self.zabbix_url = cp['zabbix']['host']
                self.datafile = cp['zabbix']['datafile']
            if cp.has_section('chat'):
                self.webhook = cp['chat'][webhook_name]
        except:
            print('Failed to read configuration file')

        self.evt_thread = self.readEventThread()
        today = datetime.datetime.now().strftime("%d-%m-%Y")
        date = {}
        date['date'] = today

        # Reset the contents of the mapping file if key value 'date' differs from current day
        try:
            if self.evt_thread['date'] and self.evt_thread['date'] != today:
                with open(self.datafile, 'w') as f:
                    json.dump(date, f)
        except:
            self.evt_thread['date'] = today
            with open(self.datafile, 'w') as f:
                json.dump(self.evt_thread, f)


    def sendMessage(self, event):
        url = self.webhook

        status = event[0]

        # Set card title and image
        stat = None
        if status == "0":
            stat = "Problem"
            image_url = self.PROBLEM_IMG
        elif status == "1":
            stat = "Resolved"
            image_url = self.RESOLVED_IMG
        elif status == "2":
            stat = "Acknowledged"
            image_url = self.ACK_IMG

        # If it is a problem or resolution message
        if status == "0" or status == "1":
            time = event[1]
            date = event[2]
            trigger_name = event[3]
            host_name = event[4]
            severity = event[5]
            self.event_id = event[6]
            trigger_url = event[7]
            self.trigger_id = event[8]
            host_description = event[9]

            bot_message = {
            "cards": [ 
              { "header": 
                { "title": "Severity: " + severity,
                  "subtitle": stat,
                  "imageUrl": image_url,
                  "imageStyle": "IMAGE"
                },
                "sections": [
                  { "widgets": [
                    { "keyValue": {
                        "topLabel": "Alarm",
                        "content": trigger_name,
                        "contentMultiline": "true"
                      }
                    },
                    { "keyValue": {
                        "topLabel": "Host",
                        "content": host_name + " " + host_description,
                        "contentMultiline": "true"
                      }
                    },
                    { "keyValue": {
                        "topLabel": "Date/Time",
                        "content": date + " - " + time
                      }
                    },
                    { "keyValue": {
                        "topLabel": "Event ID",
                        "content": self.event_id
                      }
                    }
                  ]},
                  { "widgets": [
                    { "buttons": [
                      { "textButton": 
                        { "text": "View event on ZABBIX",
                          "onClick": {
                            "openLink": {
                              "url": self.zabbix_url + "/tr_events.php?triggerid=" + self.trigger_id + "&eventid=" + self.event_id
                            }
                          }
                        }
                      }
                    ]}
                  ]}
              ]}
            ]}

        # If it is an acknowledgment message
        elif status == "2":
            time = event[1]
            date = event[2]
            ack_user = event[3]
            ack_message = event[4]
            event_status = event[5]
            self.event_id = event[6]
            self.trigger_id = event[7]

#            if event_status == "PROBLEM":
#                event_status = "Ativo"
#            elif event_status == "RESOLVED":
#                event_status = "Resolvido"

            bot_message = {
            "cards": [ 
              { "header": 
                { "title": stat,
                  "subtitle": ack_user,
                  "imageUrl": image_url,
                  "imageStyle": "IMAGE"
                },
                "sections": [
                  { "widgets": [
                    { "keyValue": {
                        "topLabel": "Message",
                        "content": ack_message,
                        "contentMultiline": "true"
                      }
                    },
                    { "keyValue": {
                        "topLabel": "Current Alarm Status",
                        "content": event_status
                      }
                    },
                    { "keyValue": {
                        "topLabel": "Date/Time",
                        "content": date + " - " + time
                      }
                    },
                    { "keyValue": {
                        "topLabel": "Event ID",
                        "content": self.event_id
                      }
                    }
                  ]},
                  { "widgets": [
                    { "buttons": [
                      { "textButton": 
                        { "text": "View event on ZABBIX",
                          "onClick": {
                            "openLink": {
                              "url": self.zabbix_url + "/tr_events.php?triggerid=" + self.trigger_id + "&eventid=" + self.event_id
                            }
                          }
                        }
                      }
                    ]}
                  ]}
              ]}
            ]}

        # Check if Event already has a thread
        if self.trigger_id in self.evt_thread:
            self.thread = self.evt_thread[self.trigger_id]
            bot_message['thread'] = { "name": self.thread }

        message_headers = { 'Content-Type': 'application/json; charset=UTF-8'}

        # HTTP API Request
        http_obj = Http()
        response = http_obj.request(
            uri=url,
            method='POST',
            headers=message_headers,
            body=dumps(bot_message),
        )

        # Take the request response thread and store
        self.thread = json.loads(response[1])['thread']['name']
        event_thread = { self.trigger_id : self.thread }
        self.writeEventThread(event_thread)

    # Reads the eventsthreads.json mapping file
    def readEventThread(self):
        try:
            with open(self.datafile) as f:
                result = json.load(f)
        except:
            result = {}
        return result

    # Writes threads to eventsthreads.json
    def writeEventThread(self, event_thread):
        content = self.readEventThread()
        if self.trigger_id not in content:
            content[self.trigger_id] = event_thread[self.trigger_id]
            with open(self.datafile, 'w') as f:
                json.dump(content, f)


if __name__ == '__main__':

    # Stores script arguments passed by Zabbix (room and message)
    webhook_name = sys.argv[1]
    msg = sys.argv[2]

    # Splits message received from Zabbix and starts processing information
    event = msg.split('#')
    cs = ChatSender(webhook_name)
    cs.sendMessage(event)



