from twisted.internet.error import ConnectionRefusedError
from twisted.internet.protocol import Protocol, ReconnectingClientFactory, ClientFactory,connectionDone


from Orses_Network_Messages.SpokenMessages import SpokenMessages, NetworkMessages


class NetworkAuditor(Protocol):

    def __init__(self, factory, conn_type):
        Protocol().__init__()
        self.factory = factory
        self.conn_type = conn_type

    def connectionMade(self):
        if self.conn_type == "check_active":  # will end connection without convo.
            self.transport.loseConnection()


class NetworkAuditorFactory(ClientFactory):

    def __init__(self, conn_type, exp_conn, q_object):
        ClientFactory().__init__()
        self.exp_conn = exp_conn
        self.q_obj = q_object
        self.dict_of_active = dict()
        self.dict_of_inactive = dict()
        self.conn_type = conn_type

    def clientConnectionLost(self, connector, reason):
        self.dict_of_active.update({connector.host: connector.port})
        if len(self.dict_of_inactive) + len(self.dict_of_active) == self.exp_conn:
            self.q_obj.put((self.dict_of_active, self.dict_of_inactive))

    def clientConnectionFailed(self, connector, reason):
        if isinstance(reason.type, type(ConnectionRefusedError)):
            self.dict_of_inactive.update({connector.host: connector.port})
        if len(self.dict_of_inactive) + len(self.dict_of_active) == self.exp_conn:
            self.q_obj.put([self.dict_of_active, self.dict_of_inactive])

    def buildProtocol(self, addr):
        return NetworkAuditor(factory=self, conn_type=self.conn_type)