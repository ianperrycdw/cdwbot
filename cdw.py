import requests
import json
import sys
import os
import hashlib
import hmac
import sys
import locale
import csv
from flask import Flask
from flask import request
# Load bot parameters from config file (excluded from GIT)
with open("botConfig.json") as json_file:
    botconfig = json.load(json_file)
    serverPort = botconfig["HEADER"]["webhookPort"]
    deploymentMode = botconfig["HEADER"]["mode"]
    app_id = botconfig["TFL"]["app_id"]
    app_key = botconfig["TFL"]["app_key"]
    webhook_key = botconfig["SPARK"]["webhook_key"]
    bearer = botconfig["SPARK"]["bot_token"]
    trustedorg = botconfig["SPARK"]["myorgID"]
webhook_key=webhook_key.encode()
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": "Bearer " + bearer
}
expected_messages = {"help me":"help" ,
                    "need help": "help",
                    "can you help me": "help",
                    "help": "help",
                    "can you help": "help",
                    "greetings": "greetings",
                    "hello": "greetings",
                    "hi": "greetings",
                    "how are you": "greetings",
                    "what's up": "greetings",
                    "what's up doc": "greetings",
                    "how you doing": "greetings",
                    "order" : "order",
                    "tube" : "tfl",
                    "travel" : "tfl",
                    "underground" : "tfl",
                    "vendor" : "vendor",
                    "partner" : "vendor",
                    "ppm" : "vendor",
                    "contact" : "vendor" }
# Initialise empty log entry
logData={'contactEmail' : '','inputText': '','actionTaken': ''}
# Load vendor contacts into array
vendorList = []
with open('vendors.csv', mode='r',encoding='utf-8') as vendorCSV:
    reader = csv.DictReader(vendorCSV)
    for line in reader:
        vendorList.append(line)

# Define Spark functions for GET and POST API calls
def send_spark_get(url, payload=None,js=True):

    if payload == None:
        request = requests.get(url, headers=headers)
    else:
        request = requests.get(url, headers=headers, params=payload)
    if js == True:
        request= request.json()
    return request


def send_spark_post(url, data):

    request = requests.post(url, json.dumps(data), headers=headers).json()
    return request


# Function to search for vendor
def findVendorContacts(vendorSearch):
    for vendor in vendorList:
        if vendorSearch.upper() in vendor['\ufeffPartner'].upper():
            vendorName = str(vendor['\ufeffPartner'])
            vendorCertificationlevel = vendor['Certification Level']
            vendorContactname = vendor['Partner Account Manager']
            vendorContactemail = vendor['PAM Email']
            vendorContactphone = vendor['PAM Phone Number']
            cdwPartnermanagername = vendor['CDW Partner Manager']
            cdwPartnermanageremail = vendor['CDW PM Email']
            cdwPartnermanagerphone = vendor['CDW PM Phone Number']
            cdwVendorstatus = vendor['Partner Status']
            return "**Vendor:** " + vendorName + "<br/>" \
            "**Contact**: " + vendorContactname + "<br/>" \
            "**E-Mail:** " + vendorContactemail + "<br/>" \
            "**Phone:** " + vendorContactphone + "<br/>" \
            "CDW is a " + vendorCertificationlevel + " partner with " + vendorName + " and we categorise them as " + cdwVendorstatus + "<br/>" \
            "They are managed by " + cdwPartnermanagername + " / " + cdwPartnermanageremail + " / " + cdwPartnermanagerphone
    return "No matching vendor found for " + vendorSearch
            

def help_me():

    return "Charlie, the CDW UK bot 🤖 <br/>" \
           "<br/>"\
           "* `Help me` - I will display what I can do.<br/>" \
           "* `tube TUBELINENAME`  - display current status of a specific underground line<br/> "\
           "* `vendor VENDORNAME` - display contact details for a CDW vendor <br/>"


def lineStatus(line):
    #First search to get proper lineID
    url = "https://api.tfl.gov.uk/Line/Search/"+line
    tflreply=requests.get(url)
    tflreply=tflreply.json()
    if tflreply["searchMatches"]:
        for data in tflreply["searchMatches"]:
            if data["mode"] == "tube":
                linename = (data["lineId"])
                print ("Found lineId of: " + linename)
                url = "https://api.tfl.gov.uk/Line/"+linename+"/Status"
                authstring = {"app_id":app_id,"app_key":app_key}
                response = requests.get(url, params=authstring)
                response = response.json()
                linename=response[0]["name"]
                for linedetails in response[0]["lineStatuses"]:
                    if linedetails["statusSeverity"] == 10:
                        userfeedback =  "👍 🚇 👍 🚇 👍 <br/>"\
                        "There is currently a good service on the " + linename + " line "
                        return userfeedback
                    else:
                        userfeedback = "⚠ 🚇 ⚠ 🚇 ⚠ <br/>"\
                        "It's not great news, TfL is reporting " + linedetails["statusSeverityDescription"] + " on the " + linename + " line <br/>" \
                        "The details of this are: <br/>"\
                        + linedetails["reason"]
                        return userfeedback
            else:
                return  " 💩 **Sorry** <br/>" \
                        "I couldn't find a matching tube line <br/>" \
                        "Try being more specific; <br/>" \
                        "' tube central' <br/>" \
                        "' tube circle'"
    else:
        print ("Didn't get anything back in search")
        return  " 💩 **Sorry** <br/>" \
                "I couldn't find a matching tube line <br/>" \
                "Try being more specific; <br/>" \
                "' tube central' <br/>" \
                "' tube circle'"
def getorgID(personID):
    requestURL='https://api.ciscospark.com/v1/people/'+personID
    personapiresponse=requests.get(requestURL,headers=headers).json()
    personorgID=personapiresponse['orgId']
    if personorgID==trustedorg:
        trusteduser=True
    else:
        trusteduser=False
    return trusteduser
app = Flask(__name__)
@app.route('/', methods=['POST'])

def spark_webhook():
    if request.method == 'POST':
        webhook = request.get_json(silent=True)
        sparksignature = request.headers.get("X-Spark-Signature")
        webhookraw = request.data
        hashed = hmac.new(webhook_key, webhookraw, hashlib.sha1)
        webhooksignature = hashed.hexdigest()
        if webhooksignature == sparksignature:
            authenticated=True
        else:
            print ("Unauthenticated HTTP POST")
            authenticated=False
        if authenticated and webhook['resource'] == "memberships" and webhook['data']['personEmail'] == bot_email:
            send_spark_post("https://api.ciscospark.com/v1/messages",
                            {
                                "roomId": webhook['data']['roomId'],
                                "markdown": (greetings() +
                                             "**Note This is a group room and you have to call "
                                             "me specifically with `@%s` for me to respond**" % bot_name)
                            }
                            )
        msg = None
        if authenticated and "@sparkbot.io" not in webhook['data']['personEmail']:
            result = send_spark_get(
                'https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
            callinguser = webhook['data']['personId']
            internaluser = getorgID(callinguser)    
            in_message = result.get('text', '').lower()
            logData.update({'contactEmail':webhook['data']['personEmail'],'inputText':in_message})
            in_message = in_message.replace(bot_name.lower() + " ", '')
            translation_table = dict.fromkeys(map(ord, '!@#$.?<>;:%^&'),None)
            in_message = in_message.translate(translation_table)
            if in_message in expected_messages and expected_messages[in_message] is "help":
                logData.update({'actionTaken':'help'})
                msg = help_me()
            elif in_message in expected_messages and expected_messages[in_message] is "rude":
                logData.update({'actionTaken':'rude'})
                msg = rude()
            elif in_message in expected_messages and expected_messages[in_message] is "order":
                if internaluser:
                    logData.update({'actionTaken':'order'})
                    msg = order()
                else:
                    logData.update({'actionTaken':'NONE-not a CDW user'})
                    msg = 'This feature is only available to CDW co-workers'
            elif in_message.startswith("tube"):
                message = in_message.split('tube ')[1]
                if len(message) > 0:
                    logData.update({'actionTaken':'tube'})
                    msg = lineStatus(message)
                else:
                    msg = "You need to put the name of a tube line after the word tube"
            elif in_message.startswith("vendor"):
                message = in_message.split('vendor ')[1]
                if len(message) > 0:
                    if internaluser:
                        logData.update({'actionTaken':'vendor'})
                        msg = findVendorContacts(message)
                    else:
                        logData.update({'actionTaken':'NONE-not a CDW user'})
                        msg = 'This feature is only available to CDW co-workers'
                else:
                    msg = 'You need to put the name of the vendor to search for'
            else:
                msg = "Sorry, but I did not understand your request. Type `Help me` to see what I can do"
            if msg != None:
                print ("Sending this text: " + msg)
                send_spark_post("https://api.ciscospark.com/v1/messages",
                                {"roomId": webhook['data']['roomId'], "markdown": msg})
            with open('logFile.json','a') as logFile:
                logFile.write(',\n')
                json.dump(logData,logFile)
        return "true"
#    elif request.method == 'GET':
#        return 
def main():
    global bot_email, bot_name
    if len(bearer) != 0:
        test_auth = send_spark_get("https://api.ciscospark.com/v1/people/me", js=False)
        if test_auth.status_code == 401:
            print("Looks like the provided access token is not correct.\n"
                  "Please review it and make sure it belongs to your bot account.\n"
                  "Do not worry if you have lost the access token. "
                  "You can always go to https://developer.ciscospark.com/apps.html "
                  "URL and generate a new access token.")
            sys.exit()
        if test_auth.status_code == 200:
            test_auth = test_auth.json()
            bot_name = test_auth.get("displayName","")
            bot_email = test_auth.get("emails","")[0]
    else:
        print("'bearer' variable is empty! \n"
              "Please populate it with bot's access token and run the script again.\n"
              "Do not worry if you have lost the access token. "
              "You can always go to https://developer.ciscospark.com/apps.html "
              "URL and generate a new access token.")
        sys.exit()

    if "@sparkbot.io" not in bot_email:
        print("You have provided an access token which does not relate to a Bot Account.\n"
              "Please change for a Bot Account access toekneview it and make sure it belongs to your bot account.\n"
              "Do not worry if you have lost the access token. "
              "You can always go to https://developer.ciscospark.com/apps.html "
              "URL and generate a new access token for your Bot.")
        sys.exit()
    else:
        app.run(host='0.0.0.0', port=serverPort)

if __name__ == "__main__":
    main()
           



        

