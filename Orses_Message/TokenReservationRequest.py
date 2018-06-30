import time, json
from Orses_Cryptography import DigitalSigner
from Crypto.Hash import SHA256


class TokenReservationRequest:

    def __init__(self, requesting_wid, time_limit=30, tokens_to_reserve=250_000, fee=1):
        """

        :param requesting_wid: hex id of wallet
        :type requesting_wid: str

        :param tokens_to_reserve: number of tokens to reserve
        :type tokens_to_reserve: float

        :param time_limit: timelimit in days
        :type time_limit: int
        """
        self.req_wid = requesting_wid
        self.tokens_to_reserve = tokens_to_reserve
        self.time_limit = time_limit  # in seconds
        self.fee = fee

    def __create_token_reservation_request(self, veri_node_proxies):
        """

        :param veri_node_proxies: a list of veri node ids (VIDs) of veri nodes that are authorized to act as proxies
                                    for
        :type veri_node_proxies: list
        :return:
        """
        #
        creation_time = int(time.time())
        tkn_rsv_req = {
            "req_wid": self.req_wid,
            "amt": self.tokens_to_reserve,
            "fee": self.fee,
            "time": creation_time,
            'exp': creation_time + self.time_limit,
            'v_node_proxies': veri_node_proxies

        }

        return tkn_rsv_req

    def sign_and_return_reservation_request(self, wallet_privkey, veri_node_proxies):

        if wallet_privkey:

            reservation_request = self.__create_token_reservation_request(veri_node_proxies=veri_node_proxies)
            print('in reservation: \n', reservation_request)

            signature = DigitalSigner.DigitalSigner.wallet_sign(message=json.dumps(reservation_request).encode(),
                                                                wallet_privkey=wallet_privkey)

            if signature is None:
                return {}
            tx_hash = SHA256.new(json.dumps(reservation_request).encode()).hexdigest()

            reservation_request_dict = {
                'rsv_req': reservation_request,
                'sig': signature,
                'tx_hash': tx_hash

            }

            return reservation_request_dict
        else:  # private key = b'' which means attempted decryption was with wrong password
            return {}


