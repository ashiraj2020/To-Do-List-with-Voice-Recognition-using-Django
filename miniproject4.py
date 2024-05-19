import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import speech_recognition as sr
import datetime
import json
import threading
import time

class TodoListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List with Voice Recognition")

        # Create a list to store tasks
        self.tasks = []

        # Create GUI elements
        self.task_entry = tk.Entry(root, width=40)
        self.task_entry.pack(pady=10)

        self.add_button = tk.Button(root, text="Add Task", command=self.add_task)
        self.add_button.pack()
        
        self.listbox = tk.Listbox(root, width=95, height=20)  
        self.listbox.pack(pady=10)
        #self.listbox = tk.Listbox(root, width=60)
        #self.listbox.pack(pady=10)

        self.delete_button = tk.Button(root, text="Delete Task", command=self.delete_task)
        self.delete_button.pack()

        self.clear_button = tk.Button(root, text="Clear All", command=self.clear_tasks)
        self.clear_button.pack()

        self.listen_button = tk.Button(root, text="Listen and Add Task", command=self.listen_and_add_task)
        self.listen_button.pack()

        self.due_date_button = tk.Button(root, text="Set Due Date", command=self.set_due_date)
        self.due_date_button.pack()

        self.save_button = tk.Button(root, text="Save Tasks", command=self.save_tasks)
        self.save_button.pack()

        # Initialize speech recognition
        self.recognizer = sr.Recognizer()

    def add_task(self):
        task = self.task_entry.get()
        if task:
            due_date = None
            self.clear_entry_field()
            due_date_str = simpledialog.askstring("Due Date", "Enter due date (YYYY-MM-DD):")
            if due_date_str:
                try:
                    due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Invalid Date", "Please enter a valid date (YYYY-MM-DD).")
                    return
            self.tasks.append({"task": task, "due_date": due_date})
            self.update_listbox()

    def delete_task(self):
        selected_task_index = self.listbox.curselection()
        if selected_task_index:
            index = selected_task_index[0]
            del self.tasks[index]
            self.update_listbox()
        elif self.tasks:
            del self.tasks[-1]
            self.update_listbox()
    def clear_tasks(self):
        self.tasks = []
        self.update_listbox()
    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        current_time = datetime.datetime.now()  # Get the current time
        for task_info in self.tasks:
            task = task_info["task"]
            due_date = task_info.get("due_date", "")
            # Format the due_date as a string without the time component
            due_date_str = due_date.strftime("%Y-%m-%d") if due_date else ""
            self.listbox.insert(tk.END, f"Task: {task} | Due Date: {due_date_str} | Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    def clear_entry_field(self):
        self.task_entry.delete(0, tk.END)

    def listen_and_add_task(self):
        try:
            with sr.Microphone() as source:
                print("Listening for task...")
                audio = self.recognizer.listen(source, timeout=5)
                task = self.recognizer.recognize_google(audio)
                if task:
                    self.task_entry.insert(tk.END, task)
                    print(f"Task added: {task}")
                else:
                    print("No task detected.")
        except sr.WaitTimeoutError:
            print("Listening timed out.")
        except sr.RequestError as e:
            print(f"Could not request results: {e}")
        except sr.UnknownValueError:
            print("Could not understand audio.")

    def set_due_date(self):
        selected_task_index = self.listbox.curselection()
        if selected_task_index:
            index = selected_task_index[0]
            due_date_str = simpledialog.askstring("Due Date", "Enter new due date (YYYY-MM-DD):")
            if due_date_str:
                try:
                    due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d")
                    self.tasks[index]["due_date"] = due_date
                    self.update_listbox()
                except ValueError:
                    messagebox.showerror("Invalid Date", "Please enter a valid date (YYYY-MM-DD).")

    def save_tasks(self):
        with open("tasks.json", "w") as file:
            task_data = [{"task": task["task"], "due_date": str(task.get("due_date", ""))} for task in self.tasks]
            json.dump(task_data, file)
        messagebox.showinfo("Save Tasks", "Tasks saved successfully!")

    def check_reminders(self):
        while True:
            current_time = datetime.datetime.now()
            for task_info in self.tasks:
                task = task_info["task"]
                due_date = task_info.get("due_date")
                if due_date and current_time >= due_date:
                    messagebox.showinfo("Task Reminder", f"Task '{task}' is due!")
            time.sleep(60)  # Check every minute

def main():
    root = tk.Tk()
    app = TodoListApp(root)
    reminder_thread = threading.Thread(target=app.check_reminders)
    reminder_thread.daemon = True
    reminder_thread.start()
    root.mainloop()

if __name__ == "__main__":
    main()

