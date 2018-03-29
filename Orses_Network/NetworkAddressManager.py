from Orses_Util.FileAction import FileAction
import Orses_Util.Filenames_VariableNames as filenames


class NetworkAddressManager:
    """
    Class will contain variables and methods to create, update, return and manage network addresses
    This includes creating an addresses file
    Updating and addresses file, when new addresses are discovered
    returning addresses to a NetworkManager method, when client must connect to the network
    managing addresses, by checking calculating dependability of addresses and sending msgs to those first
    managing addresses by knowing which addresses are Contestant node ( possible block creators) and which are req
    """

    def __init__(self, username=None):

        self.address_dict = dict()
        self.active_peers = dict()
        self.inactive_peers = dict()
        self.exp_conn = 0
        if username:
            self.set_address_list(username=username)

        self.is_default = False

    def update_address_list(self, username, new_addresses):
        pass

    def set_active_peers(self, dict_of_active_peers):
        self.active_peers = dict_of_active_peers

    def set_inactive_peers(self, dict_of_inactive_peers):
        self.inactive_peers = dict_of_inactive_peers

    def set_address_list(self, username):

        addr_dict = FileAction.open_file_from_json(
            filename=filenames.username_address_list.format(username),
            in_folder=filenames.network_data_folder
        )

        self.is_default = False if addr_dict else True  # will set default to True if no file with username found
        self.address_dict = addr_dict if addr_dict else self.get_default_address_list()
        self.active_peers = self.address_dict
        self.exp_conn = len(self.address_dict)

    def get_address_list(self):
        """
        get list of addresss list
        :return: list: [['ip address', portnumber], ['ip address', portnumber]]
        """

        return self.address_dict

    def get_active_peers(self):
        """
        used to return active peers
        active peers == address_list Until check_active_peers is called (usually after signing into a wallet)
        if no active after checking for active peers, user must manually update (find using search engine)
        :return:
        """

        return self.active_peers

    def get_inactive_peers(self):
        """
        used to return inactive peers
        inactive empty until checked, could be empty if all active
        :return:
        """

        return self.inactive_peers

    def create_address_list(self, username, dict_of_address):

        FileAction.save_json_into_file(
            filename=filenames.username_address_list.format(username),
            python_json_serializable_object=dict_of_address,
            in_folder=filenames.network_data_folder
        )

        return True


    @staticmethod
    def get_default_address_list():

        addr_list = FileAction.open_file_from_json(
            filename=filenames.default_addr_list,
            in_folder="CryptoHub_Network"
        )

        return addr_list




if __name__ == '__main__':
    n = NetworkAddressManager(username="sam")

    print(n.address_list, n.exp_conn)