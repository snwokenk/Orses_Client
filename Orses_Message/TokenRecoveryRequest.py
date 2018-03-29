"""
Allows you to use your client info (id, pub/priv key) to recover tokens from a wallet
in which the private key has been lost. This is Not for compromised wallet because tokens must still be
associated with wallet (in wallet).

With a Token recovery request tokens are sent from one wallet to another wallet with the signature of client id,
BOTH WALLETS MUST BE OWNED BY THE SAME CLIENT ID
"""


class TokenRecoveryRequest:
    pass