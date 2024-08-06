import datetime
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import default
from deploy_locale import *
import requests
import json
from Login import LoginApp

data = default.DefaultApp()
login_obj = LoginApp()


class QuizApp:

    def QnA(self):
        data.default()
        screen_width = data.screen_width
        screen_height = data.screen_height
        current_question_index = 0

        # To get the question through vercel api
        try:
            quiz_data_api_url = "https://flask-quiz-app-xi.vercel.app/"
            # local_server_url = "http://127.0.0.1:7777/getQuestions"
            response = requests.get(quiz_data_api_url)
            if response.status_code == 200:
                print("Questions Data Received !!!")
                quiz_question_data = json.loads(response.text)
                
        except Exception as e:
            print("Cannot retrieve questions !!!" , e)

        questions = quiz_question_data['questions'][:5]
        options = quiz_question_data['options'][:5]
        correct_answers = quiz_question_data['correct_answers'][:5]


        user_answers = [""] * len(questions)
        canvas = tk.Canvas(data.root, bg="#fff")
        canvas.pack(side="left", fill="both", expand=True)

        bg = Image.open("./Assets/Qna-bg.png")
        bgimg = ImageTk.PhotoImage(bg.resize((screen_width, screen_height)))

        def update_image(event=None):
            canvas.config(width=screen_width, height=screen_height)
            canvas.create_image(0, 0, image=bgimg, anchor="nw")

        data.root.bind("<Configure>",update_image)

        content_frame = tk.Frame(
            canvas,
            bg="#fff",
            borderwidth=1,
            relief="solid",
        )
        content_frame.pack(fill="both", padx=100, pady=100)

        def auto_width(text, min_width=10):
            required_width = max(len(text), min_width)
            return required_width

        def widgets():

            for widget in content_frame.winfo_children():
                widget.destroy()

            question = questions[current_question_index]
            option = options[current_question_index]

            que_label = tk.Label(
                content_frame,
                text=f"Question {current_question_index+1}:",
                font=(data.font, 14),
                wraplength=screen_width,
                anchor="w",
                justify="left",
                bg="#fff",
            )
            que_label.pack(padx=20, pady=(50, 50), anchor="w")

            que_text = tk.Label(
                content_frame,
                text=question,
                font=(data.font, 14),
                width=auto_width(question),
                wraplength=screen_width - 30,
                anchor="w",
                justify="left",
                bg="#fff",
            )
            que_text.pack(padx=20, pady=(10, 50), anchor="w")

            selected_option = tk.StringVar(value=user_answers[current_question_index])

            def select_option(value):
                selected_option.set(value)
                user_answers[current_question_index] = value
                widgets()

            for opt in option:
                is_selected = opt == selected_option.get()
                tk.Radiobutton(
                    content_frame,
                    text=f" {opt} ",
                    font=(data.font, 14),
                    value=opt,
                    variable=selected_option,
                    indicatoron=False,
                    selectcolor="green",
                    wraplength=screen_width - 40,
                    fg=(
                        "white" if is_selected else "black"
                    ),  # Change text color if selected
                    bg=(
                        "green" if is_selected else "#fff"
                    ),  # Change background color if selected
                    command=lambda val=opt: select_option(val),
                ).pack(padx=20, pady=10, anchor="w")

            button_frame = tk.Frame(content_frame, bg="#fff")
            button_frame.pack(fill="both", expand=True, pady=(100, 20), side="bottom")

            def prev_question():
                nonlocal current_question_index
                if current_question_index > 0:
                    user_answers[current_question_index] = selected_option.get()
                    current_question_index -= 1
                    widgets()

            def next_question():
                if not selected_option.get():
                    messagebox.showerror(
                        "Error", "Please select an answer before proceeding."
                    )
                else:
                    nonlocal current_question_index
                    if current_question_index < len(questions) - 1:
                        user_answers[current_question_index] = selected_option.get()
                        selected_ans = user_answers[current_question_index]
                        current_question_index += 1
                        que_ans = f"{current_question_index} = {selected_ans}"
                        transaction_id = deploy_data("B","-",que_ans,"-")
                        student_data = {
                            "wallet_address": wallet_address,
                            "booklet": "B",
                            "start_time": "-",
                            "que_ans": que_ans,
                            "end_time": "-",
                            "transaction_id": transaction_id
                        }
                        print("Sending student data:", student_data)
                        login_obj.add_student_data(student_data)
                        selected_option.set("")
                        widgets()

            prev_button = tk.Button(
                button_frame,
                text="Previous",
                bg="#D68A78",
                fg="#fff",
                font=(data.font, 14),
                relief="raised",
                command=prev_question,
            )
            prev_button.pack(side="left", padx=20)

            next_button = tk.Button(
                button_frame,
                text="Next",
                bg="#D68A78",
                fg="#fff",
                font=(data.font, 14),
                relief="raised",
                command=next_question
            )
            next_button.pack(side="right", padx=20)

            def thank_you():
                for widget in content_frame.winfo_children():
                    widget.destroy()

                thank_you_label = tk.Label(
                    content_frame,
                    text="Thank you for taking the exam!",
                    font=(data.font, 20),
                    bg="#fff",
                )
                thank_you_label.pack(pady=20)

                # Additional information
                info_label = tk.Label(
                    content_frame,
                    text="Your responses have been saved.",
                    font=(data.font, 16),
                    bg="#fff",
                )
                info_label.pack(pady=10)

                # Additional decoration or text
                decoration_label = tk.Label(
                    content_frame,
                    text="You may now close this window.",
                    font=(data.font, 16),
                    bg="#fff",
                    fg="green",
                )
                decoration_label.pack(pady=10)

                # Add a button to close the window
                close_button = tk.Button(
                    content_frame,
                    text="Close",
                    bg="#D68A78",
                    fg="#fff",
                    font=(data.font, 14),
                    relief="raised",
                    command=data.root.quit,
                )
                close_button.pack(pady=20)

            def Final_Sub():
                user_answers[current_question_index] = (
                    selected_option.get()
                )  
                sc = sum(
                    1
                    for i, answer in enumerate(user_answers)
                    if answer == correct_answers[i]
                )
                total_questions = len(questions)
                percentage_score = (sc / total_questions) * 100

                answer = messagebox.askquestion(
                    "Confirm", "Confirm you want to submit answers?"
                )
                if answer == "yes":
                    selected_ans = user_answers[current_question_index]
                    que_ans = f"{current_question_index+1} = {selected_ans}"
                    transaction_id=deploy_data("B","-",que_ans,"-")
                    student_data = {
                            "wallet_address": wallet_address,
                            "booklet": "B",
                            "start_time": "-",
                            "que_ans": que_ans,
                            "end_time": "-",
                            "transaction_id": transaction_id
                        }
                    login_obj.add_student_data(student_data)
                    current_time = datetime.datetime.now()
                    date_str = f"{current_time.day}/{current_time.month}/{current_time.year}"
                    time_str = f"{current_time.hour}:{current_time.minute}:{current_time.second}"
                    end_time = f"{date_str} {time_str}"
                    transaction_id = deploy_data("B","-","-",end_time)
                    student_data = {
                            "wallet_address": wallet_address,
                            "booklet": "B",
                            "start_time": "-",
                            "que_ans": "-",
                            "end_time": end_time,
                            "transaction_id": transaction_id
                        }
                    login_obj.add_student_data(student_data)
                    print("Before removing :- " , get_wallet_address())
                    remove_wallet_address()
                    try :
                        print(get_wallet_address())
                    except:
                        print("Wallet deleted")

                    for widget in content_frame.winfo_children():
                        widget.destroy()
                    
                    score_text = tk.Label(
                        content_frame,
                        text="Your score for the current exam is:",
                        font=(data.font, 14),
                        width=auto_width("Your score for the current exam is:"),
                        wraplength=screen_width - 30,
                        bg="#fff",
                    )
                    score_text.pack(pady=(50, 20))

                    score = tk.Label(
                        content_frame,
                        text=f"{sc}/{len(questions)}",
                        font=(data.font, 16),
                        width=auto_width(f"{sc}/{len(questions)}"),
                        wraplength=screen_width - 30,
                        bg="#fff",
                        fg="green",
                    )
                    score.pack(pady=20)
                   
                    tot = tk.Label(
                        content_frame,
                        text=f"{percentage_score}%",
                        font=(data.font, 16),
                        width=auto_width(f"{percentage_score}%"),
                        wraplength=screen_width - 30,
                        bg="#fff",
                        fg="green",
                    )
                    tot.pack(pady=20)

                    done_button = tk.Button(
                        content_frame,
                        text="Done",
                        bg="#D68A78",
                        fg="#fff",
                        font=(data.font, 14),
                        relief="raised",
                        command=thank_you,
                    )
                    done_button.pack(pady=20)

            if current_question_index == 0:
                prev_button.pack_forget()

            if current_question_index == len(questions) - 1:
                next_button.pack_forget()
                final_submit = tk.Button(
                    button_frame,
                    text="Submit Exam",
                    bg="green",
                    fg="#fff",
                    font=(data.font, 14),
                    relief="raised",
                    command=Final_Sub,
                )
                final_submit.pack(side="right", padx=20)

        widgets()
