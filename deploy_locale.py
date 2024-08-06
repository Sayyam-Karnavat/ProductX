import base64
import logging
import algokit_utils
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from artifact_file import HelloWorldClient

logger = logging.getLogger(__name__)

algod_address = "http://localhost:4001"
algod_token = "a" * 64
indexer_add = "http://localhost:8980"
algod_client = AlgodClient(algod_token, algod_address)
indexer_client = IndexerClient(algod_token, indexer_add)
deployer = algokit_utils.get_localnet_default_account(algod_client)

app_client = HelloWorldClient(
    algod_client,
    creator=deployer,
    indexer_client=indexer_client,
)
print(deployer)
wallet_address = deployer.address

app_client.deploy(
    on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
    on_update=algokit_utils.OnUpdate.AppendApp,
)
print(app_client.app_id)

def deploy_data(booklet,start_time,que_ans,end_time):
    response = app_client.quiz_data(
        wallet_address=wallet_address,
        booklet=booklet,
        start_time=start_time,
        que_ans=que_ans,
        end_time=end_time,
    )
    # print(f"wallet_address: {wallet_address},\nbooklate: {booklet},\nstart_time: {start_time},\nque_ans: {que_ans},\nend_time: {end_time}")
    # print(response.tx_info)
    

    global_state_delta = response.tx_info['global-state-delta']
    for delta in global_state_delta:
        key = delta['key']
        value = delta['value']['bytes']
        
        # Decode the key from base64 to a readable format (if necessary)
        decoded_key = base64.b64decode(key).decode('utf-8')
        decoded_value = base64.b64decode(value).decode('utf-8')
        print(f"{decoded_key} : {decoded_value}")
        
    transaction_id = response.tx_id
    print("Transaction ID: ",transaction_id)
    return transaction_id


def remove_wallet_address():
    global wallet_address
    wallet_address = None

def get_wallet_address():
    return wallet_address
       


