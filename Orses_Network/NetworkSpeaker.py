# from twisted.internet import reactor
from twisted.internet.error import ConnectionRefusedError
from twisted.internet.protocol import Protocol, ReconnectingClientFactory,connectionDone

from Orses_Network_Messages.SpokenMessages import SpokenMessages, NetworkMessages

"""
The goal for the NetworkSpeaker protocol and factory is to be used to send network messages.
A simplified approach will be taken, in which the job of these classes are only to connect to other nodes in 
the network and set the message object instance variable to the instance of NetworkSpeaker passed on by factory.

1. The classes in this file will be instantiated by methods in the NetworkManager class 
    in folder "CryptoHub_Network"
2. The classes in this file will be instantiated with a message object(depending on the type of message)
3. This message object for a client protocol/factory will be a "Speaker" message object and will manage network 
    conversations with a "Listener" message object of a server protocol/factory

 
"""


class NetworkSpeaker(Protocol):
    """
    class used by client software to 'speak' to the network
    """

    def __init__(self, message_object, factory):
        """
        :param factory: instance of factory creating this protocol class
        :param message_object: an instance of the SpokenMessages class
                                (must have speak(), listen(), follow_up())
        implemented
        """
        Protocol().__init__()
        self.factory = factory
        self.message_object = message_object
        assert (isinstance(self.message_object, SpokenMessages))

    def dataReceived(self, data):

        # listens and appends msg to list in self.message_object
        self.message_object.listen(data)

        # if end_convo is true then ends connection
        if self.message_object.end_convo:
            self.transport.loseConnection()
        else:
            # speaks to other node, before speaking checks listen list
            self.transport.write(self.message_object.speak())

    def connectionMade(self):
        self.transport.write(self.message_object.speak())
        self.factory.total_connected += 1

    def connectionLost(self, reason=connectionDone):
        self.message_object.follow_up()
        print("connection lost", self.message_object.messages_heard[-1] == b'ver')
        if self.message_object.messages_heard[-1] == b'ver':
            self.factory.total_verified += 1
        elif self.message_object.messages_heard[-1] == b'rej':
            self.factory.total_rejected += 1
        else:
            self.factory.total_rejected += 1


class NetworkSpeakerFactory(ReconnectingClientFactory):
    """
    creates instances of NetworkSpeaker class for each connection

    """

    def __init__(self, spkn_msg_obj_creator, queue_obj, exp_conn):
        ReconnectingClientFactory().__init__()
        self.message_object = spkn_msg_obj_creator
        self.maxRetries = 1
        self.exp_conn = exp_conn
        self.total_connected = 0
        self.total_verified = 0
        self.total_rejected = 0
        self.total_conn_fail = 0
        self.q_object = queue_obj

    def clientConnectionLost(self, connector, reason):

        # checks if all addresses has been tried and either connected of failed to connect (after retry)
        # then returns the percentage connections verifying msg vs expected connection
        self.check_if_all_connections_tried()

    def clientConnectionFailed(self, connector, reason):
        """
        default port is 55600, if connection failed  and reason is connection refused then try to port 55601
        :param connector:
        :param reason:
        :return:
        """

        # print("is type: ", isinstance(reason.type, type(ConnectionRefusedError)))
        print(vars(reason))

        # check to see if reason is for connection refused, tries port 55601 once,
        if isinstance(reason.type, type(ConnectionRefusedError)):
            print("trying again")
            connector.port = 55601
            if self.retries < self.maxRetries:
                connector.connect()
            else:
                self.total_conn_fail += 1
                self.check_if_all_connections_tried()

            self.retries += 1
        else:
            self.retries = self.maxRetries+1  # makes self.retries maximum allowed, stopping any retry
            self.total_conn_fail += 1
            self.check_if_all_connections_tried()

    def check_if_all_connections_tried(self):
        """
        use to check if all addresses tried and if so, returns ratio of connections that verified message vs
        expected connections
        :return:
        """

        if self.total_connected + self.total_conn_fail == self.exp_conn:
            if self.total_verified:
                self.q_object.put(self.total_verified/self.exp_conn)
            else:
                print("all connections tried")
                self.q_object.put(0.00)

    def buildProtocol(self, addr):
        return NetworkSpeaker(message_object=self.message_object(), factory=self)


if __name__ == '__main__':
    pass
    # msg = NetworkMessages.message_to_be_spoken_creator(main_msg=b'samuel')
    # factory = NetworkSpeakerFactory(spkn_msg_obj_creator=msg)
    # reactor.connectTCP(host="127.0.0.1", port=50000, factory=factory)
    # reactor.run()