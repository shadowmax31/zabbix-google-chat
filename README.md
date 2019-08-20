# zabbix-google-chat
Python script to send Zabbix notifications to Hangouts Chat (G Suite).

Guidelines on how to use this code are available at:

https://medium.com/monitoracaodeti/enviando-notifica%C3%A7%C3%B5es-do-zabbix-via-api-do-hangouts-chat-aa0c0e8197a1

## Testing

./google_chat.py Monitoring 1#{EVENT.RECOVERY.TIME}#{EVENT.RECOVERY.DATE}#{TRIGGER.NAME}#{HOST.NAME}#{TRIGGER.SEVERITY}#{EVENT.ID}#{TRIGGER.URL}#{TRIGGER.ID}#- {HOST.DESCRIPTION}
