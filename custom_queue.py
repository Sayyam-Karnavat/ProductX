from collections import deque
import time
import threading
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
import algokit_utils
from artifact_file import HelloWorldClient

class taskQueue:
    def __init__(self) -> None:
        self.task_queue = deque()

    def add_task(self , start_time , end_time , booklet , question_no , answer ):
        self.single_task = {
            "starttime" : start_time,
            "endtime": end_time,
            "booklet" : booklet,
            "question_number" : question_no,
            "answer" : answer
        }
        # Since it is a queue we want first come first server functionality
        self.task_queue.appendleft(self.single_task)

        print(f"Task appended  !!!{self.single_task}")

        return 1


    def complete_task(self):

        if len(self.task_queue)> 0:
            # Take the last value since it is the first pushed in queue
            task_data = self.task_queue[-1]

            print(f"Executing task {task_data}")
            startTime = task_data['starttime']
            endTime = task_data['endtime']
            Booklet = task_data['booklet']
            Question_Number = task_data['question_number']
            Answer = task_data['answer']

            # Write blockchain data 
            deploy(starttime= startTime , endtime= endTime , booklet= Booklet , question_number= Question_Number , answer= Answer)

            print("Task completed ... Removing it from queue!!!")
            # Once data is being deployed remove that task from queue
            self.remove_task()
            return 1
        else:
            return 0
    
    def remove_task(self):
        removed_task = self.task_queue.pop()
        print(f"Task removed from queue{removed_task}")
        return removed_task


    def get_all_tasks(self):
        return self.task_queue if len(self.task_queue) else "No task in queue"




def deploy( starttime , endtime , booklet , question_number , answer):

    algod_url = "http://localhost:4001"
    algod_token = "a" * 64
    indexer_url = "http://localhost:8980"


    # Testnet URl :- https://testnet-api.algonode.cloud - Algod Server URL
    # Testne indexer :- https://testnet-idx.algonode.cloud - Indexer URL

    algod_client = AlgodClient(algod_token=algod_token,algod_address=algod_url)
    indexer_client = IndexerClient("",indexer_address= indexer_url)

    
    
    deployer = algokit_utils.get_account(algod_client ,name="" ,fund_with_algos= 1000)
    print(f"Deployer address :- {deployer.address}")

    app_client = HelloWorldClient(
        algod_client,
        creator=deployer,
        indexer_client=indexer_client,
    )
    app_client.app_id = 1004

    # app_client.deploy(
    #     on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
    #     on_update=algokit_utils.OnUpdate.AppendApp,
    # )
    
    response = app_client.write_quiz_data(start_time=starttime, end_time=endtime , booklet=booklet , question_no=question_number, answer= answer)
    print(f"Transaction ID :- {response.tx_id}")
    print(f"App ID :- {app_client.app_id}")



def GUI_Response(obj):
    # Thread 1 (This thread will be of user Response from GUI)
    for i in range(10):
        obj.add_task(start_time=f"starttime{i}" , 
                     end_time= f"endtime{i}" , 
                     booklet=f"booklet{i}",
                     question_no=f"question{i}",
                     answer=f"answer{i}")
        i+=1
        time.sleep(3)

def complete_tasks(obj):
    while True:
        obj.complete_task()
        time.sleep(2)

if __name__ == "__main__":

    queue_obj = taskQueue()

    # Insert thread 
    thread1 = threading.Thread(target= GUI_Response , args=(queue_obj,))
    thread2 = threading.Thread(target= complete_tasks , args=(queue_obj,))

    
    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()