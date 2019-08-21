# zabbix-google-chat
Python script to send Zabbix notifications to Hangouts Chat (G Suite).

Guidelines on how to use this code are available at:

https://medium.com/monitoracaodeti/enviando-notifica%C3%A7%C3%B5es-do-zabbix-via-api-do-hangouts-chat-aa0c0e8197a1

## Setup

    cd `zabbix_server -h | grep alertscripts | awk -F\" '{print $2}'`
    git clone https://github.com/ctrl-freak/zabbix-google-chat.git
    cd zabbix-google-chat
    cp google_chat.example.ini google_chat.ini
    chmod + x google_chat.py
    chown zabbix:zabbix google_chat.py google_chat.ini eventsthreads.json

## Create Google Hangouts Chat Room

- Click on the search field to have Chat display options and click on “Create Room”:
- Name the room
- With the room created, click on its name in the top left and then “Set up webhooks”:
- Provide a name for the bot and, if desired, the URL of an image for the bot:
- Clicking save the API will provide the webhook address you created. Copy and save this address, as this is where Zabbix will know which Chat room to send notifications to:

## Configuring Zabbix

* Administration, Media types; Create media type
  - Name: Google Hangouts Chat
  - Type: Script
  - Script name: zabbix-google-chat/google_chat.py
  - Script parameters:
    - {ALERT.SENDTO}
    - {ALERT.MESSAGE}
* Adinistration, Users; Create user
  - Alias: hangouts.chat
  - Name: Google Hangouts Chat
  - Groups: No access to the frontend
  - Media tab; Add
    - Type: Google Chat
    - Send to: <Webhook Name>
    - Enabled: Yes
  - Permissions tab
    - User type: Zabbix Super Admin
* Configuration, Actions; Create action
  - Action tab
    - Name: Google Hangouts Chat
  - Operations tab
    - Default message: `0#{EVENT.TIME}#{EVENT.DATE}#{EVENT.NAME}#{HOST.NAME}#{EVENT.SEVERITY}#{EVENT.ID}#{TRIGGER.URL}#{TRIGGER.ID}#- {HOST.DESCRIPTION}`
    - Operations, New:
      - Operation type: Send message
      - Sent to Users: hangouts.chat
      - Send only to: Google Hangouts Chat
  - Recovery operations tab
    - Default message: `1#{EVENT.RECOVERY.TIME}#{EVENT.RECOVERY.DATE}#{EVENT.NAME}#{HOST.NAME}#{EVENT.SEVERITY}#{EVENT.ID}#{TRIGGER.URL}#- {HOST.DESCRIPTION}`
    - Operations, New
      - Notify everyone involved
  - Update operations tab
    - Default message: `2#{EVENT.UPDATE.TIME}#{EVENT.UPDATE.DATE}#{USER.FULLNAME}#{EVENT.UPDATE.MESSAGE}#{EVENT.ACK.STATUS}#{EVENT.ID}#{TRIGGER.ID}`
    - Operations, New
      - Notify everyone involved

## Testing

./google_chat.py Monitoring 1#{EVENT.RECOVERY.TIME}#{EVENT.RECOVERY.DATE}#{TRIGGER.NAME}#{HOST.NAME}#{TRIGGER.SEVERITY}#{EVENT.ID}#{TRIGGER.URL}#{TRIGGER.ID}#- {HOST.DESCRIPTION}
