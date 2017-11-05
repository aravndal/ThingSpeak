from modules import cbpi
from thread import start_new_thread
import logging
import urllib, json, httplib, requests

DEBUG = False
thingspeak_api = None
thingspeak_chnid = None
ubidots_token = None
ubidots_label = None
thingspeak_ok = None
thingspeak_api_write = None
drop_first = None

def log(s):
    if DEBUG:
        s = "IOT: " + s
        cbpi.app.logger.info(s)

def httpCon(url, path='', data_load='', meth='GET'):
    log("%s to URL %s - %s - %s" % (meth, url, path, data_load))
    try:
        data_load = eval(data_load)
        params = urllib.urlencode(data_load)
        conn = httplib.HTTPSConnection(url)
        path += "?" + params if params != "" else ""
        log("Path: %s" % path)
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
        cbpi.notify("IOT Error", "Check API and Channel ID.", type="danger", timeout=10000)
    return False

def httpJSON(url, path='', param='', data=''):
    log("URL %s - %s - %s, json %s" % (url, path, param, data))
    param = eval(param)
    params = urllib.urlencode(param)
    url += path
    url += "?" + params if params != "" else ""
    headers = {'content-type': 'application/json'}
    log("URL: %s, JSON: %s" % (url, data))
    try:
        response = requests.post(url, data=data, headers=headers)
        log("response %s" % response)
        return response
    except:
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

def ubidotsLabel():
    global ubidots_label
    ubidots_label = cbpi.get_config_parameter("ubidots_label", None)
    if ubidots_label is None:
        log("Init Ubidots Config Label ID")
        try:
            cbpi.add_config_parameter("ubidots_label", "", "text", "Ubidots API Label")
        except:
            cbpi.notify("Ubidots Error", "Unable to update config parameter", type="danger")

def ubidotsAPI():
    global ubidots_token
    ubidots_token = cbpi.get_config_parameter("ubidots_token", None)
    if ubidots_token is None:
        log("Init Ubidots Token")
        try:
            cbpi.add_config_parameter("ubidots_token", "", "text", "Ubidots API Token")
        except:
            cbpi.notify("Ubidots Error", "Unable to update config parameter", type="danger")

def Fillfield(jsonstr, key, value):
    data = ""
    if key in jsonstr:
        data = ", '%s':'%s'" % (key, value) if jsonstr[key] == "" else ""
    else:
        data = ", '%s':'%s'" % (key, value)
    return data

def thingspeakFields():
    global thingspeak_ok
    global thingspeak_api
    global thingspeak_api_write
    url = "api.thingspeak.com"
    if (thingspeak_api == "" or thingspeak_chnid == ""):
        log("ThingSpeak Config error")
        cbpi.notify("ThingSpeak Error", "Please update config parameter", type="danger")
        return False
    brewery_name = cbpi.get_config_parameter("brewery_name", "CraftBeerPi")
    data_api = "{'api_key':'%s'" % thingspeak_api
    path = "/channels/%s.json" % thingspeak_chnid
    result = httpCon(url, path, data_api+"}")
    log("JSON: %s" % result)
    data = ""
    data += Fillfield(result, "tags", "Brew, CraftBeerPi, Beer, RaspBerryPi")
    data += Fillfield(result, "description", "The CraftBeerPi temperature sensor logging for the brewery %s." % brewery_name)
    path = "/channels/%s/feeds.json" % thingspeak_chnid
    result = httpCon(url, path, data_api+", 'results':'0'}")
    log("JSON: %s" % result)
    path = "/channels/%s.json" % thingspeak_chnid
    cnt = 1
    for key, value in cbpi.cache.get("sensors").iteritems():
        field = 'field%s' % cnt
        try:
            data += Fillfield(result["channel"], field, value.name)
        except:
            data += Fillfield({}, field, value.name)
        cnt += 1
    data += "}"
    data = data_api + data
    result = httpCon(url, path, data, 'PUT')
    thingspeak_api_write = result["api_keys"][0]["api_key"]
    log("API Write: %s" % thingspeak_api_write)

@cbpi.initalizer(order=9000)
def init(cbpi):
    cbpi.app.logger.info("ThingSpeak plugin Initialize")
    thingspeakAPI()
    thingspeakChnID()
    ubidotsAPI()
    ubidotsLabel()
    if thingspeakAPI is None:
        cbpi.notify("ThingSpeak Error", "API key missing for ThingSpeak plugin, please update and reboot", type="danger")
    if thingspeakChnID is None:
        cbpi.notify("ThingSpeak Error", "Channel ID missing for ThingSpeak plugin, please update and reboot", type="danger")

def ThingspeakUpdate(data):
    global thingspeak_ok
    global drop_first
    url = "api.thingspeak.com"
    if thingspeak_ok is None:
        thingspeakFields()
        thingspeak_ok = True
    if (thingspeak_api_write == ""):
        log("ThingSpeak Write API not got from site")
        cbpi.notify("ThingSpeak Error", "Please try to update config parameter and reboot.", type="danger")
        return False
    path = "/update.json"
    data_api = "{'api_key':'%s'" % thingspeak_api_write
    data = data_api + data
    result = httpCon(url, path, data)

def UbidotsUpdate(data):
    global ubidots_token
    global ubidots_label
    log("Ubidots update")
    url = "http://things.ubidots.com"
    if (ubidots_token == "" or ubidots_label == ""):
        log("Ubidots Token or label incorrect")
        cbpi.notify("Ubidots Error", "Please try to update config parameter and reboot.", type="danger")
        return False
    for count, (key, value) in enumerate(cbpi.cache["kettle"].iteritems(), 1):
        if value.target_temp is not None:
            data += ", \"target_temp_%s\":%s" % (count,value.target_temp)
    for count, (key, value) in enumerate(cbpi.cache["actors"].iteritems(), 1):
        if value.state is not None:
            data += ", \"actor_%s\":%s" % (value.name,value.state)
    data += "}"
    path = "/api/v1.6/devices/%s/" % ubidots_label
    param = "{'token':'%s'}" % ubidots_token
    result = httpJSON(url, path, param, data)

@cbpi.backgroundtask(key="thingspeak_task", interval=60)
def thingspeak_background_task(api):
    log("IOT background task")
    global drop_first
    if drop_first is None:
        drop_first = False
        return False
    cnt = 1
    dataT= ""
    dataU= "{"
    for key, value in cbpi.cache.get("sensors").iteritems():
        dataT += ", 'field%s':'%s'" % (cnt, value.instance.last_value)
        dataU += ", " if key >1 else ""
        dataU += "\"%s\":%s" % (value.name, value.instance.last_value)
        cnt += 1
    dataT += "}"
    log("Thing")
    ThingspeakUpdate(dataT)
    log("Ubidots")
    UbidotsUpdate(dataU)

