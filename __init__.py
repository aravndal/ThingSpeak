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
        s = "ThingSpeak: " + s
        cbpi.app.logger.info(s)

def httpCon(path='', data_load='', meth='GET'):
    global url
    log("%s to URL %s - %s - %s" % (meth, url, path, data_load))
    try:
        params = urllib.urlencode(data_load)
        conn = httplib.HTTPSConnection(url)
        path += "?" + params if params != "" else ""
        conn.request(meth, path)
        response = conn.getresponse()
        try:
            json_result = response.read()
            json_result = json.loads(json_result)
            return json_result
        except Exception as e:
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

def Fillfield(jsonstr, key, value):
    data = ""
    if key in jsonstr:
        data = ", '%s':'%s'" % (key, value) if jsonstr[key] == "" else ""
    return data

def thingspeakFields():
    global thingspeak_ok
    global thingspeak_api
    global thingspeak_api_write
    cnt = 1
    if (thingspeak_api == "" or thingspeak_chnid == ""):
        log("ThingSpeak Config error")
        cbpi.notify("ThingSpeak Error", "Please update config parameter", type="danger")
        return False
    brewery_name = cbpi.get_config_parameter("brewery_name", "CraftBeerPi")
    path = "/channels/%s.json" % thingspeak_chnid
    result = httpCon(path)
    log("JSON: %s" % result)
    data_api = "{'api_key':'%s'" % thingspeak_api
    data = ""
    data += Fillfield(result, "name", brewery_name)
    data += Fillfield(result, "tags", "Brew, CraftBeerPi, Beer, RaspBerryPi")
    data += Fillfield(result, "description", "The CraftBeerPi temperature sensor logging for the brewery %s." % brewery_name)
    path = "/channels/%s/feeds.json?results=0" % thingspeak_chnid
    result = httpCon(path)
    log("JSON: %s" % result)
    path = "/channels/%s.json" % thingspeak_chnid
    tst = ""
    for key, value in cbpi.cache.get("sensors").iteritems():
        field = 'field%s' % cnt
        data += Fillfield(result["channel"], field, value.name)
        cnt += 1
    data += "}"
    data = data_api + data
    data = eval(data)
    result = httpCon(path, data, 'PUT')
    thingspeak_api_write = result["api_keys"][0]["api_key"]
    log("API Write: %s" % thingspeak_api_write)

@cbpi.initalizer(order=9000)
def init(cbpi):
    cbpi.app.logger.info("ThingSpeak plugin Initialize")
    thingspeakAPI()
    thingspeakChnID()
    if thingspeakAPI is None:
        cbpi.notify("ThingSpeak Error", "API key missing for ThingSpeak plugin, please update and reboot", type="danger")
    if thingspeakChnID is None:
        cbpi.notify("ThingSpeak Error", "Channel ID missing for ThingSpeak plugin, please update and reboot", type="danger")

@cbpi.backgroundtask(key="thingspeak_task", interval=20)
def thingspeak_background_task(api):
    global thingspeak_ok
    global drop_first
    log("ThingSpeak background task")
    if thingspeak_ok is None:
        thingspeakFields()
        thingspeak_ok = True
    if drop_first is None:
        drop_first = False
        return False
    if (thingspeak_api_write == ""):
        log("ThingSpeak Write API not got from site")
        cbpi.notify("ThingSpeak Error", "Please try to update config parameter and reboot.", type="danger")
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
    result = httpCon(path, data)
    log("URL Result: %s" % result.read())

