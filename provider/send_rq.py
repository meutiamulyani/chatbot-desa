import requests

class ResponseHandler():
    url ="https://api.fonnte.com/send"
    def __init__(self):
        pass

    def sendMsg(self, to, message):
        payload = {
            'target': to,
            'message': message
        }

        files=[]
        headers = {
            'Authorization': 'j#ao_dX1JFfF8hAUsNXM'
        }

        response = requests.request("POST", ResponseHandler.url, headers=headers, data=payload, files=files)
    
    def sendAttach(self, to, message, attachment):
        payload = {
            'target': to,
            'message': message
        }

        files=[]
        headers = {
            'Authorization': 'j#ao_dX1JFfF8hAUsNXM'
        }

        response = requests.request("POST", ResponseHandler.url, headers=headers, data=payload, files=files)        