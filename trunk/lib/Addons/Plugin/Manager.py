from Communication.AcceptServer import CAcceptServer
from Communication.SocketWrapper import CSocketWrapper
from Communication.ComSpec import *
from Interface.Core import CCore
from Interface.Transaction import CTransaction
from Interface.Classes.base import IBase
from lib.consts import *
from Watchdog import CWatchdog
import thread

class CPluginManager(object):
    '''
    Class that provides management for plugins, their connections
    
    There should be only one instance of this class in application
    '''

    def __init__(self, pluginAdapter):
        IBase.SetAdapter(pluginAdapter)
        self.pluginlock = thread.allocate()
        self.plugins = {}
        self.conlock = thread.allocate()
        self.connection = {}
        self.transaction = {}
        self.addr2uri = {}
        self.pluginAdapter = pluginAdapter
        pluginAdapter._SetPluginManager(self)
        self.proxy = CCore(self, pluginAdapter)
        self.watchdog = CWatchdog(self)
        if PLUGIN_SOCKET is not None:
            self.acceptserver = CAcceptServer(('localhost', PLUGIN_SOCKET), self.NewConnection)
            self.acceptserver.Start()
    
    def NewConnection(self, sock, addr):
        '''
        callback from acceptserver
        
        @param sock: connected socket from plugin
        @param addr: identifier of connection
        '''
        with self.conlock:
            self.transaction[addr] = CTransaction()
            self.connection[addr] = CSocketWrapper(sock, self.proxy, addr, True)
    
    def AddPlugin(self, plugin):
        with self.pluginlock:
            uri = plugin.GetUri()
            if uri in self.plugins:
                raise Exception() # TODO: replace with better exception
            self.plugins[uri] = plugin
            plugin._SetPluginManager(self)
    
    def ConnectPlugin(self, uri, addr):
        with self.pluginlock:
            if self.plugins[uri].IsInitialized():
                raise Exception() # TODO: replace with better exception
            
            self.addr2uri[addr] = uri
            self.plugins[uri]._Connect(addr)
    
    def GetGuiManager(self):
        '''
        @return: GuiManager instance
        '''
        return self.pluginAdapter.GetGuiManager()
    
    def GetPluginAdapter(self):
        return self.pluginAdapter
    
    def Send(self, addr, code, **params):
        with self.conlock:
            if addr not in self.connection:
                return
            if self.connection[addr].Opened():
                self.connection[addr].Send(code, '', params)
            else:
                del self.connection[addr]
            
    
    def SendToAll(self, code, **params):
        with self.conlock:
            for addr in self.connection.keys(): #this must use list, not iterator (beware in python 3.x)
                self.Send(addr, code, **params)
            
    def GetPort(self):
        if PLUGIN_SOCKET is not None:
            return self.acceptserver.GetPort()
        else:
            return None
    
    def GetTransaction(self, addr):
        return self.transaction[addr]
    
    def GetPluginList(self):
        with self.pluginlock:
            return list(self.plugins.itervalues()) 
        #this is required to return list because it is used 
        # for iteration and is likely to change
    
    def RemovePlugin(self, plugin):
        plugin.IsAlive()
        self.__removePlugin(plugin.GetUri(), plugin.GetAddr())
    
    def __removePlugin(self, uri, addr):
        with self.pluginlock:
            with self.conlock:
                if uri in self.plugins:
                    self.plugins[uri].IsAlive() #just to make sure that process won't remain zombie
                    del self.plugins[uri]
                if addr in self.connection:
                    self.connection[addr].Close()
                    del self.connection[addr]
    
    def RemoveByAddr(self, addr):
        self.__removePlugin(self.addr2uri.get(addr, None), addr)
        
        self.GetGuiManager().DisposeOf(addr)
        
    def Stop(self):
        self.watchdog.Stop()
        if PLUGIN_SOCKET is not None:
            self.acceptserver.Stop()
    
    def Addr2Uri(self, addr):
        return self.addr2uri.get(addr, None)
            
    
