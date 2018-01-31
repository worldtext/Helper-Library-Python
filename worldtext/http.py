# coding=UTF8

from urllib2 import Request, urlopen, URLError
import urllib
import json
import logging
import worldtext


class WorldTextSMS:
   def __init__(self):
      if worldtext.api_key is None:
         raise Exception("worldtext.api_key is not set")
      if worldtext.account_id is None:
         raise Exception("worldtext.account_id is not set")
      self.id = worldtext.account_id
      self.key = worldtext.api_key
      self.auth = "id={}&key={}".format(self.id, self.key)
      self.baseurl = "https://sms.world-text.com/v2.0/"
      self.gsm7bitChars = "@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà"
      self.gsm7bitExChar = "^{}\\[~]|€"
   

   def getError(self):
      """Returns a tuple with the error code, reason and interface response"""
      return (self.error, self.error_desc)


   def request(self, request, args={}, method="GET"):
      args['id'] = self.id
      args['key'] = self.key
      if worldtext.sim is not None:
         args['sim'] = True
      args['method'] = method
      argstr = urllib.urlencode(args)
      url = self.baseurl + request + "?" + argstr
      try:
         logging.debug(url)
         response = urlopen(url)
         logging.debug(response)
         data = response.read().rstrip()
         return json.loads(data)
      except URLError, e:
         self.error = str(e)
         self.error_desc = None
         if e.code == 400:
            self.error_desc = json.loads(e.read())['desc']
         logging.error(self.error + ": " + self.error_desc)
         return None


   def isUCS(self, data):
      for c in data:
         if c not in self.gsm7bitChars and c not in self.gsm7bitExChar:
            return True
      return False


class Admin(WorldTextSMS):
   def __init__(self):
      WorldTextSMS.__init__(self)

   def credits(self):
      data = self.request("admin/credits")
      if data is not None:
         return data['credits']
      else:
         return None

   def ping(self):
      if self.request("admin/ping")['status'] == '0':
         return True
      else:
         return False


class SMS(WorldTextSMS):
   def __init__(self):
      WorldTextSMS.__init__(self)

   def cost(self, dstaddr):
      data = self.request("sms/cost", {"dstaddr":dstaddr})
      if data is not None:
         return data['credits']
      else:
         return None

   def send(self, dstaddr, txt, srcaddr = "", sendid = ""):
      args = {'dstaddr':dstaddr, 'txt':txt}
      if sendid != "":
         args['sendid'] = sendid
      if srcaddr != "":
         args['srcaddr'] = srcaddr

      if self.isUCS(txt):
         args['enc'] = "UnicodeBigUnmarked"

      data = self.request("sms/send", args, "PUT")
      if data is not None:
         return data
      else:
         return None


class Group(WorldTextSMS):
   def __init__(self, accountid, apikey):
      WorldTextSMS.__init__(self, accountid, apikey)

   def add(self, grpid, dstaddr, name = ""):
      """Adds a single name/number pair to a group, the number (dstaddr) must be unique within the group."""
      args = {"grpid":grpid,"dstaddr":dstaddr}
      if name != "":
         args['name'] = name
      data = self.request("group/entry", args, "PUT")
      if data is not None:
         return data
      else:
         return None

   def cost(self, grpid):
      """Returns the number of credits a single text message would cost to send to every number in the group"""
      data = self.request("group/cost", {"grpid":grpid})
      if data is not None:
         return data
      else:
         return None

   def create(self,name,pin,srcaddr = "WorldText"):
      """Creates a group to allow sending of a text message to all numbers in the group at once"""
      data = self.request("group/create", {"pin":pin,"srcaddr":srcaddr,"name":name}, "PUT")
      if data is not None:
         return data
      else:
         return None

   def destroy(self, grpid):
      """Removes a pre-existing group"""
      data = self.request("group/destroy", {"grpid":grpid}, "DELETE")
      if data is not None:
         return data
      else:
         return None

   def delete(self, grpid, dstaddr):
      """Deletes a single entry from a group"""
      data = self.request("group/entry", {"grpid":grpid,"dstaddr":dstaddr}, "DELETE")
      if data is not None:
         return data
      else:
         return None

   def details(self, grpid):
      """Returns all the name and number pairs in the given group."""
      data = self.request("group/details", {"grpid":grpid})
      if data is not None:
         return data
      else:
         return None

   def empty(self, grpid):
      """Deletes ALL the names and numbers in the specified group."""
      data = self.request("group/contents", {"grpid":grpid}, "DELETE")
      if data is not None:
         return data
      else:
         return None

   def list(self):
      """List all groups currently stored on this account."""
      data = self.request("group/list")
      if data is not None:
         return data
      else:
         return None

   def send(self, grpid, txt):
      """Sends an SMS Text message to a group"""
      args = {'grpid':grpid, 'txt':txt}
      if self.isUCS(txt):
         args['enc'] = "UnicodeBigUnmarked"
      data = self.request("group/send", args, "PUT")
      if data is not None:
         return data
      else:
         return None


