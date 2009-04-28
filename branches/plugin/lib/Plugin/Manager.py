from Communication.AcceptServer import CAcceptServer
from Communication.SocketWrapper import CSocketWrapper
from Communication.ComSpec import *
from Proxy import CProxy
from lib.consts import *
from lib.Gui import CGuiManager
import thread

class CPluginManager(object):
    '''
    Class that provides management for plugins, their connections
    
    There should be only one instance of this class in application
    '''

    def __init__(self, app):
        self.conlock = thread.allocate()
        self.connection = {}
        self.app = app
        self.guimanager = CGuiManager(app)
        self.proxy = CProxy(self, app)
        self.acceptserver = CAcceptServer(('localhost', PLUGIN_SOCKET), self.NewConnection)
        self.acceptserver.Start()
        print "PORT:", self.acceptserver.sock.getsockname()[1]
    
    def NewConnection(self, sock, addr):
        '''
        callback from acceptserver
        
        @param sock: connected socket from plugin
        @param addr: identifier of connection
        '''
        try:
            self.conlock.acquire()
            self.connection[addr] = CSocketWrapper(sock, self.proxy, addr, True)
        finally:
            self.conlock.release()
    
    def GetGuiManager(self):
        '''
        @return: GuiManager instance
        '''
        return self.guimanager
    
    def Send(self, addr, code, **params):
        if addr not in self.connection:
            return
        if self.connection[addr].Opened():
            self.connection[addr].Send(code, '', params)
        else:
            del self.connection[addr]
    
    def SendToAll(self, code, **params):
        try:
            self.conlock.acquire()
            for addr in self.connection.keys(): #this must use list, not iterator (beware in python 3.x)
                self.Send(addr, code, **params)
        finally:
            self.conlock.release()
    
    def DomainValueChanged(self, element, path):
        self.SendToAll(RESP_DOMAIN_VALUE_CHANGED, element = r_object(element), path = path)
    
