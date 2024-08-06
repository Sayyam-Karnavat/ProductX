import base64
from artifact_file import HelloWorldClient
import algokit_utils
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from algosdk import account,mnemonic,transaction

# Create a deployer
# Create the client
algod_address = "https://testnet-api.algonode.cloud"
algod_token = "a" * 64
indexer_add = "https://testnet-idx.algonode.cloud"
algod_client = AlgodClient(algod_token, algod_address)
indexer_client = IndexerClient("", indexer_add)

#create account
private_key, address = account.generate_account()
new_mnemonic = mnemonic.from_private_key(private_key)

deployer = algokit_utils.get_account_from_mnemonic(new_mnemonic)

wallet_address = deployer.address
transaction_id = ""

app_client = HelloWorldClient(
    algod_client, creator=deployer, indexer_client=indexer_client
)

def funded_account():
    # Funded Account
    master_wallet = mnemonic.to_private_key("banner enlist wide have awake rail resource antique arch tonight pilot abuse file metal canvas beyond antique apart giant once slight ice beef able uncle")
    master_addr = account.address_from_private_key(master_wallet)
    # print(master_addr)
    amount_microalgos = int(0.5 * 1e6)
    # print(amount_microalgos)
    suggested_params = algod_client.suggested_params()
    txn = transaction.PaymentTxn(
        sender=master_addr,
        receiver=wallet_address,
        amt=amount_microalgos,
        sp=suggested_params
    )
    signed_txn = txn.sign(master_wallet)
    txid = algod_client.send_transaction(signed_txn)
    print(f"Funded Transaction ID: {txid}")

funded_account()

# Create app client to use the app the we have deployed 
app_client.deploy(
    on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
    on_update=algokit_utils.OnUpdate.AppendApp,
)

def deploy_data(booklet,start_time,que_ans,end_time):
    # print(
    #     f"Deployer address: {deployer.address}\nDeployer privateKey: {deployer.private_key}"
    # )
    # print("Mnemonic", new_mnemonic)
    # print("Private key", private_key)
    # print("Address", address)
    # app_client.app_id = 675696144
    # print("App ID:", app_client.app_id)

    # wallet_address = wallet_address
    # booklate = "sample booklet"
    # start_time = "14 : 47 : 43"
    # que_ans = "1:D"
    # end_time = "14 : 47 : 43"
    response = app_client.quiz_data(
        wallet_address=wallet_address,
        booklet=booklet,
        start_time=start_time,
        que_ans=que_ans,
        end_time=end_time,
    )
    # print(f"wallet_address: {wallet_address},\nbooklate: {booklate},\nstart_time: {start_time},\nque_ans: {que_ans},\nend_time: {end_time}")
    # print(response.tx_info)
    

    global_state_delta = response.tx_info['global-state-delta']
    for delta in global_state_delta:
        key = delta['key']
        value = delta['value']['bytes']
        
        # Decode the key from base64 to a readable format (if necessary)
        decoded_key = base64.b64decode(key).decode('utf-8')
        decoded_value = base64.b64decode(value).decode('utf-8')
        # print(f"{decoded_key} : {decoded_value}")
    
    transaction_id = response.tx_id
    print("Transaction ID: ",transaction_id)
    return transaction_id
       
def remove_wallet_address():
    global wallet_address
    wallet_address = None

def get_wallet_address():
    return wallet_address

# if __name__ == "__main__":
#     deploy_data()
