import collections


class SpokenMessages:
    """
    Base class for different types of messages.

    This allows one to easily add a message type by creating the messages to be sent (or sequence of messages to be
    sent

    In this case, to nodes, a sender and receiver speak to each other using an iterator self.messages_to_be_spoken.
    the Speak() method is used to send data and listen() method is used to append to self.messages_heard list
    Before speaking, each node checks to see if the other node has sent an end, reject or verified message

    """

    def __init__(self, messages_to_be_spoken, wallet_pubkey):
        """


        :param messages_to_be_spoken: non-dict iterable (list, set, tuple) of bytes/byte string message ie b'hello'
        """
        assert (isinstance(messages_to_be_spoken, collections.Iterable)), "first argument of SpokenMessages Class must " \
                                                                          "be and iterable (list, set, tuple) "
        self.wallet_pubkey = wallet_pubkey.encode()
        self.messages_to_be_spoken = iter(messages_to_be_spoken)

        self.messages_heard = list()
        self.last_msg = b'end'
        self.reject_msg = b'rej'
        self.verified_msg = b'ver'
        self.end_convo = False

    def speak(self):
        """
        For veri nodes must override this method not to look for rejection or acceptance msg
        :return:
        """
        try:
            if self.messages_heard and self.messages_heard[-1] in {self.last_msg, self.reject_msg, self.verified_msg}:
                self.end_convo = True
                return self.last_msg
            elif self.messages_heard and self.messages_heard[-1] == b'wpk':  # if veri node does not have wallet pubkey
                return self.wallet_pubkey
            return next(self.messages_to_be_spoken)

        except StopIteration:
            self.end_convo = True
            return self.last_msg

    def listen(self, msg):
        """
        in Protocol().dataReceived() listen() must come first before speak() (for both client and server(listener node)
        in Protocol().connectionMade() the client
        :param msg: append into self.message_heard list
        :return: None
        """
        self.messages_heard.append(msg)

    def follow_up(self):
        """
        call this function in Protocol.connectionLost()
        this function generally stores messages in database of message. while storing it notes if the message
        was verified, rejected or incomplete (connection was closed or lost)
        :return:
        """
        pass


class NetworkMessages:
    """
    class is used to store static methods that return a list for use SpokenMessages class
    in attribute messages_to_be_spoken.

    This is done by using the NetworkManager class.
    """

    @staticmethod
    def message_to_be_spoken_creator(main_msg, wallet_pubkey, initial_msg=b'rcn', reason_msg=b'tx_asg'):
        """

        :param main_msg: byte string, main message
        :type main_msg: bytes
        :param initial_msg: byte string, initial message
        :param reason_msg: byte sring, reason message
        :return: a callable, the callable can be used to return a list
        """
        # print("main msg: ", main_msg, "\ntype: ", type(main_msg))

        def spoken_msg_create():
            return SpokenMessages([initial_msg, reason_msg, main_msg], wallet_pubkey=wallet_pubkey)

        return spoken_msg_create  # returns the callable Not the iterable
