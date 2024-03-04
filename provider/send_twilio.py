from twilio.rest import Client

def TwilioNewConnection():
    account_sid = 'AC7baad6ae28c3ec80db3ecceb2508fade'
    auth_token = '34c2f16521622d9568e95aa9114592fa'
    client = Client(account_sid, auth_token)
    return client

class TwilioHandler():
    client = None
    def __init__(self):
        account_sid = 'AC7baad6ae28c3ec80db3ecceb2508fade'
        auth_token = '34c2f16521622d9568e95aa9114592fa'
        TwilioHandler.client = Client(account_sid, auth_token)

    def sendMsg(self, to, message):
        TwilioHandler.client.messages.create(
            from_='whatsapp:+14155238886',
            body=message,
            to=to
        )
    
    # def sendCS(self, to, message):
    #     TwilioHandler.client.messages.create(
    #         from_=
    #     )