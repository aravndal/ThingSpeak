from modules import cbpi
from thread import start_new_thread
import logging
import urllib, json, httplib

DEBUG = False
thingspeak_api = None
thingspeak_chnid = None
thingspeak_ok = None
thingspeak_api_write = None
drop_first = None
url = "api.thingspeak.com"

def log(s):
    if DEBUG:
        cbpi.app.logger.info(s)

def httpCon(url, path, data_load, meth='GET'):
    log("%s to URL %s - %s - %s" % (meth, url, path, data_load))
    try:
        params = urllib.urlencode(data_load)
        conn = httplib.HTTPSConnection(url)
        path += "?" + params
        log("Path: %s" % path)
        conn.request(meth, path)
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
    global thingspeak_api_write
    global url
    cnt = 1
    if (thingspeak_api == "" or thingspeak_api == ""):
        log("ThingSpeak Config error")
        cbpi.notify("ThingSpeak Error", "Please update config parameter", type="danger")
        return False
    brewery_name = cbpi.get_config_parameter("brewery_name", "CraftBeerPi")
    path = "/channels/%s.json" % thingspeak_chnid
    data_api = "{'api_key':'%s'" % thingspeak_api
    data = ", 'name':'%s'" % brewery_name
    data += ", 'tags':'Brew, CraftBeerPi, Beer, RaspBerryPi'"
    for key, value in cbpi.cache.get("sensors").iteritems():
        data += ", 'field%s':'%s'" % (cnt, value.name)
        cnt += 1
    data += "}"
    data = data_api + data
    data = eval(data)
    result = httpCon(url, path, data, 'PUT')
    json_result = result.read()
    json_result = json.loads(json_result)
    thingspeak_api_write = json_result["api_keys"][0]["api_key"]
    log("API Write: %s" % thingspeak_api_write)
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

@cbpi.backgroundtask(key="thingspeak_task", interval=60)
def thingspeak_background_task(api):
    global thingspeak_ok
    global url
    global drop_first
    log("ThingSpeak background task")
    if thingspeak_ok is None:
        thingspeakFields()
    # YOUR CODE GOES HERE
    if drop_first is None:
        drop_first = False
        return False
    if (thingspeak_api == "" or thingspeak_api == ""):
        log("ThingSpeak Config error")
        cbpi.notify("ThingSpeak Error", "Please update config parameter", type="danger")
        return False
    cnt = 1
    path = "/update.json"
    data_api = "{'api_key':'%s'" % thingspeak_api_write
    data = ""
    for key, value in cbpi.cache.get("sensors").iteritems():
        data += ", 'field%s':'%s'" % (cnt, value.instance.last_value)
        cnt += 1
    data += "}"
    data = data_api + data
    data = eval(data)
    result = httpCon(url, path, data)
    log("URL Result: %s" % result.read())

