from modules import cbpi
from thread import start_new_thread
import logging
import urllib, json, httplib

DEBUG = True
thingspeak_api = None 
thingspeak_chnid = None
thingspeak_ok = None

def log(s):
    if DEBUG:
        cbpi.app.logger.info(s)

def httpPOST(url, path, data_load):
    log("PUT to URL %s - %s - %s" % (url, path, data_load))
    try:
        params = urllib.urlencode(data_load)
        conn = httplib.HTTPSConnection(url)
        path += "?" + params
        conn.request('PUT', path)
        response = conn.getresponse()
        return response
    except Exception as e:
        cbpi.app.logger.error("FAILED when contacting site: %s" % (url))
        cbpi.notify("ThingSpeak Error", "Check API and Channel ID.", type="danger", timeout=10000)
    return False

def thingspeakAPI():
    global thingspeak_api
    thingspeak_api = cbpi.get_config_parameter("thingspeak_api", None)
    if thingspeak_api is None:
        log("Init ThingSpeak Config API Key")
        try:
            cbpi.add_config_parameter("thingspeak_api", "", "text", "ThingSpeak USER API key")
        except:
            cbpi.notify("ThingSpeak Error", "Unable to update config parameter", type="danger")

def thingspeakChnID():
    global thingspeak_chnid
    thingspeak_chnid = cbpi.get_config_parameter("thingspeak_chnid", None)
    if thingspeak_chnid is None:
        log("Init ThingSpeak Config Channel ID")
        try:
            cbpi.add_config_parameter("thingspeak_chnid", "", "text", "ThingSpeak Channel ID")
        except:
            cbpi.notify("ThingSpeak Error", "Unable to update config parameter", type="danger")

def thingspeakFields():
    global thingspeak_ok
    global thingspeak_api
    cnt = 1
    if (thingspeak_api == "" or thingspeak_api == ""):
        log("ThingSpeak Config error")
        cbpi.notify("ThingSpeak Error", "Please update config parameter", type="danger")
        return False
    for key, value in cbpi.cache.get("sensors").iteritems():
        url = "api.thingspeak.com"
        path = "/channels/%s.json" % thingspeak_chnid
        log(url)
        data = "{'api_key':'%s', 'field%s':'%s'}" % (thingspeak_api, cnt, value.name)
        log(data)
        data = eval(data)
        log(data)
        result = httpPOST(url, path, data)
        log("URL Result: %s" % result.read())
        cnt += 1
    thingspeak_ok = True

@cbpi.initalizer(order=9000)
def init(cbpi):
    log("Initialize ThingSpeak Plugin")
    thingspeakAPI()
    thingspeakChnID()
    if thingspeakAPI is None:
        cbpi.notify("ThingSpeak Error", "API key missing for ThingSpeak plugin, please update and reboot", type="danger")
    if thingspeakChnID is None:
        cbpi.notify("ThingSpeak Error", "Channel ID missing for ThingSpeak plugin, please update and reboot", type="danger")

@cbpi.backgroundtask(key="thingspeak_task", interval=10)
def thingspeak_background_task(api):
    global thingspeak_ok
    log("ThingSpeak background task")
    if thingspeak_ok is None:
        thingspeakFields()
    # YOUR CODE GOES HERE
    if (thingspeak_api == "" or thingspeak_api == ""):
        log("ThingSpeak Config error")
        cbpi.notify("ThingSpeak Error", "Please update config parameter", type="danger")
        return False
    for key, value in cbpi.cache.get("sensors").iteritems():
        log(key)
        log(value)
        log(value.name)
        log(value.instance.get_unit())
        log(value.instance.last_value)

