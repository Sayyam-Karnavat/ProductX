import datetime
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import default
from deploy_locale import *
import requests
import json
from Login import LoginApp
from queue import Queue
import threading
import time

class taskQueue:
    def __init__(self) -> None:
        self.task_queue = Queue()

    def add_task(self, start_time, end_time, booklet, question_no, answer):
        single_task = {
            "starttime": start_time,
            "endtime": end_time,
            "booklet": booklet,
            "question_number": question_no,
            "answer": answer
        }
        self.task_queue.put(single_task)
        # print(f"Task appended: {single_task}")
        # print(f"Queue size after appending: {self.task_queue.qsize()}")
        return 1

    def complete_task(self):
        if not self.task_queue.empty():
            task_data = self.task_queue.get()
            # print(f"Executing task: {task_data}")
            startTime = task_data['starttime']
            endTime = task_data['endtime']
            Booklet = task_data['booklet']
            Question_Number = task_data['question_number']
            Answer = task_data['answer']

            question_and_answer = f"{Question_Number} - {Answer}"

            deploy_data(start_time=startTime, end_time=endTime, booklet=Booklet, que_ans=question_and_answer)

            print("Task completed and removed from queue.")
            print(f"New queue size: {self.task_queue.qsize()}")
            return 1
        else:
            return 0

    def get_all_tasks(self):
        return list(self.task_queue.queue) if not self.task_queue.empty() else "No task in queue"

class QuizApp:
    def __init__(self):
        self.data = default.DefaultApp()
        self.login_obj = LoginApp()
        self.stopEvent = threading.Event()
        self.queue_obj = taskQueue()

        complete_task_thread = threading.Thread(target=self.complete_tasks, args=(self.queue_obj,))
        complete_task_thread.start()
    
    def complete_tasks(self, obj):
        while not self.stopEvent.is_set():
            obj.complete_task()
            time.sleep(0.5)

    def QnA(self):
        self.data.default()
        self.screen_width = self.data.screen_width
        self.screen_height = self.data.screen_height
        self.current_question_index = 0

        try:
            quiz_data_api_url = "https://flask-quiz-app-xi.vercel.app/"
            response = requests.get(quiz_data_api_url)
            if response.status_code == 200:
                print("Questions Data Received !!!")
                quiz_question_data = json.loads(response.text)
        except Exception as e:
            print("Cannot retrieve questions !!!", e)

        self.questions = quiz_question_data['questions'][:5]
        self.options = quiz_question_data['options'][:5]
        self.correct_answers = quiz_question_data['correct_answers'][:5]

        self.user_answers = [""] * len(self.questions)
        self.canvas = tk.Canvas(self.data.root, bg="#fff")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.bg = Image.open("./Assets/Qna-bg.png")
        self.bgimg = ImageTk.PhotoImage(self.bg.resize((self.screen_width, self.screen_height)))

        self.data.root.bind("<Configure>", self.update_image)

        self.content_frame = tk.Frame(
            self.canvas,
            bg="#fff",
            borderwidth=1,
            relief="solid",
        )
        self.content_frame.pack(fill="both", padx=100, pady=100)

        self.widgets()

    def update_image(self, event=None):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        self.canvas.create_image(0, 0, image=self.bgimg, anchor="nw")

    def auto_width(self, text, min_width=10):
        required_width = max(len(text), min_width)
        return required_width

    def widgets(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        question = self.questions[self.current_question_index]
        option = self.options[self.current_question_index]

        que_label = tk.Label(
            self.content_frame,
            text=f"Question {self.current_question_index+1}:",
            font=(self.data.font, 14),
            wraplength=self.screen_width,
            anchor="w",
            justify="left",
            bg="#fff",
        )
        que_label.pack(padx=20, pady=(50, 50), anchor="w")

        que_text = tk.Label(
            self.content_frame,
            text=question,
            font=(self.data.font, 14),
            width=self.auto_width(question),
            wraplength=self.screen_width - 30,
            anchor="w",
            justify="left",
            bg="#fff",
        )
        que_text.pack(padx=20, pady=(10, 50), anchor="w")

        self.selected_option = tk.StringVar(value=self.user_answers[self.current_question_index])

        for opt in option:
            is_selected = opt == self.selected_option.get()
            tk.Radiobutton(
                self.content_frame,
                text=f" {opt} ",
                font=(self.data.font, 14),
                value=opt,
                variable=self.selected_option,
                indicatoron=False,
                selectcolor="green",
                wraplength=self.screen_width - 40,
                fg=("white" if is_selected else "black"),
                bg=("green" if is_selected else "#fff"),
                command=lambda val=opt: self.select_option(val),
            ).pack(padx=20, pady=10, anchor="w")

        self.create_navigation_buttons()

    def select_option(self, value):
        self.selected_option.set(value)
        self.user_answers[self.current_question_index] = value
        self.widgets()

    def prev_question(self):
        if self.current_question_index > 0:
            self.user_answers[self.current_question_index] = self.selected_option.get()
            self.current_question_index -= 1
            self.widgets()

    def next_question(self):
        if not self.selected_option.get():
            messagebox.showerror("Error", "Please select an answer before proceeding.")
        else:
            if self.current_question_index < len(self.questions) :
                self.user_answers[self.current_question_index] = self.selected_option.get()
                selected_ans = self.user_answers[self.current_question_index]
                self.current_question_index += 1
                que_ans = f"{self.current_question_index} = {selected_ans}"

                self.queue_obj.add_task(start_time="-" , end_time="-" , booklet="B" , question_no = self.current_question_index  , answer = selected_ans )

                student_data = {
                    "wallet_address": wallet_address,
                    "booklet": "B",
                    "start_time": "-",
                    "que_ans": que_ans,
                    "end_time": "-",
                    "transaction_id": "transaction_id"
                }
                # print("Sending student data:", student_data)
                # self.login_obj.add_student_data(student_data)
                self.selected_option.set("")
                self.widgets()

    def thank_you(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        thank_you_label = tk.Label(
            self.content_frame,
            text="Thank you for taking the exam!",
            font=(self.data.font, 20),
            bg="#fff",
        )
        thank_you_label.pack(pady=20)

        info_label = tk.Label(
            self.content_frame,
            text="Your responses have been saved.",
            font=(self.data.font, 16),
            bg="#fff",
        )
        info_label.pack(pady=10)

        decoration_label = tk.Label(
            self.content_frame,
            text="You may now close this window.",
            font=(self.data.font, 16),
            bg="#fff",
            fg="green",
        )
        decoration_label.pack(pady=10)
        close_button = tk.Button(
            self.content_frame,
            text="Close",
            bg="#D68A78",
            fg="#fff",
            font=(self.data.font, 14),
            relief="raised",
            command=self.data.root.quit,
        )
        close_button.pack(pady=20)

    def check_queue(self):
        while True :
            if not self.queue_obj.task_queue.empty() :
                messagebox.showwarning("Transactions Pending", "The transactions are yet to be written. Do not close this window!")
            else:
                self.stopEvent.set()
                messagebox.showinfo("All Transactions Written", "You can safely close this window")
                break

    def Final_Sub(self):
        sc = sum(
            1
            for i, answer in enumerate(self.user_answers)
            if answer == self.correct_answers[i]
        )
        total_questions = len(self.questions)
        percentage_score = (sc / total_questions) * 100
        answer = messagebox.askquestion(
            "Confirm", "Confirm you want to submit answers?"
        )
        if answer == "yes":

            # Since it is a last question answer and our login "next_question" goes only upto (len(question)-1 ) we did "self.current_question_index+1"
            self.user_answers[self.current_question_index] = self.selected_option.get()
            selected_ans = self.user_answers[self.current_question_index]
            que_ans = f"{self.current_question_index+1} = {selected_ans}"

            print(f"Last question asnwer :- {que_ans}")
            self.queue_obj.add_task(start_time="-" , end_time="-" , booklet="B" , question_no =self.current_question_index+1  , answer = selected_ans )
            
            # student_data = {
            #     "wallet_address": wallet_address,
            #     "booklet": "B",
            #     "start_time": "-",
            #     "que_ans": que_ans,
            #     "end_time": "-",
            #     "transaction_id": "transaction_id"
            # }
            # self.login_obj.add_student_data(student_data)
            current_time = datetime.datetime.now()
            date_str = f"{current_time.day}/{current_time.month}/{current_time.year}"
            time_str = f"{current_time.hour}:{current_time.minute}:{current_time.second}"
            end_time = f"{date_str} {time_str}"
            self.queue_obj.add_task(start_time="-" , end_time=end_time , booklet="B" , question_no = "-"  , answer = "-" )
            self.check_queue()
            student_data = {
                "wallet_address": wallet_address,
                "booklet": "B",
                "start_time": "-",
                "que_ans": "-",
                "end_time": end_time,
                "transaction_id": "transaction_id"
            }

            # self.login_obj.add_student_data(student_data)
            print("Before removing:", get_wallet_address())
            remove_wallet_address()
            
            try:
                print(get_wallet_address())
            except:
                print("Wallet deleted")

            for widget in self.content_frame.winfo_children():
                widget.destroy()

            score_text = tk.Label(
                self.content_frame,
                text="Your score for the current exam is:",
                font=(self.data.font, 14),
                width=self.auto_width("Your score for the current exam is:"),
                wraplength=self.screen_width - 30,
                bg="#fff",
            )
            score_text.pack(pady=(50, 20))

            score = tk.Label(
                self.content_frame,
                text=f"{sc}/{len(self.questions)}",
                font=(self.data.font, 16),
                width=self.auto_width(f"{sc}/{len(self.questions)}"),
                wraplength=self.screen_width - 30,
                bg="#fff",
                fg="green",
            )
            score.pack(pady=20)

            tot = tk.Label(
                self.content_frame,
                text=f"{percentage_score}%",
                font=(self.data.font, 16),
                width=self.auto_width(f"{percentage_score}%"),
                wraplength=self.screen_width - 30,
                bg="#fff",
                fg="green",
            )
            tot.pack(pady=20)

            done_button = tk.Button(
                self.content_frame,
                text="Done",
                bg="#D68A78",
                fg="#fff",
                font=(self.data.font, 14),
                relief="raised",
                command=self.thank_you,
            )
            done_button.pack(pady=20)

    def create_navigation_buttons(self):
        button_frame = tk.Frame(self.content_frame, bg="#fff")
        button_frame.pack(fill="both", expand=True, pady=(100, 20), side="bottom")

        prev_button = tk.Button(
            button_frame,
            text="Previous",
            bg="#D68A78",
            fg="#fff",
            font=(self.data.font, 14),
            relief="raised",
            command=self.prev_question,
        )
        prev_button.pack(side="left", padx=20)

        next_button = tk.Button(
            button_frame,
            text="Next",
            bg="#D68A78",
            fg="#fff",
            font=(self.data.font, 14),
            relief="raised",
            command=self.next_question
        )
        next_button.pack(side="right", padx=20)

        if self.current_question_index == 0:
            prev_button.pack_forget()

        if self.current_question_index == len(self.questions) - 1:
            next_button.pack_forget()
            final_submit = tk.Button(
                button_frame,
                text="Submit Exam",
                bg="green",
                fg="#fff",
                font=(self.data.font, 14),
                relief="raised",
                command=self.Final_Sub,
            )
            final_submit.pack(side="right", padx=20)
