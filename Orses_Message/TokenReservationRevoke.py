import time, json
from Orses_Cryptography import DigitalSigner
from Crypto.Hash import SHA256


class TokenReservationRevoke:
    """
    {
    rvk_req: {
            req_wid: str,
            fee: float/real,
            trr_hash: str,
            },
    sig: base85 string
    tx_hash: sha256 hex hash
    }
    """
    def __init__(self, tx_hash_trr, fee, requesting_wid):

        self.req_wid = requesting_wid
        self.fee = fee
        self.tx_hash_trr = tx_hash_trr

    def __create_token_revoke_request(self, veri_node_proxies):
        """

        :param veri_node_proxies: a list of veri node ids (VIDs) of veri nodes that are authorized to act as proxies
                                    for
        :type veri_node_proxies: list
        :return:
        """

        creation_time = int(time.time())

        tkn_rvk = {
            "req_wid": self.req_wid,
            "trr_hash": self.tx_hash_trr,
            "fee": self.fee,
            "time": creation_time,
            "v_node_proxies": veri_node_proxies
        }

        return tkn_rvk

    def sign_and_return_revoke_request(self, wallet_privkey, veri_node_proxies):

        if wallet_privkey:
            revoke_request = self.__create_token_revoke_request(veri_node_proxies=veri_node_proxies)
            print('in revoke: \n', revoke_request)

            signature = DigitalSigner.DigitalSigner.wallet_sign(message=json.dumps(revoke_request).encode(),
                                                                wallet_privkey=wallet_privkey)
            tx_hash = SHA256.new(json.dumps(revoke_request).encode()).hexdigest()

            revoke_request_dict = {
                'rvk_req': revoke_request,
                'sig': signature,
                'tx_hash': tx_hash

            }

            return revoke_request_dict
        else:  # private key = b'' which means attempted decryption was with wrong password
            return {}