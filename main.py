import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk  # Importujemy ttk do Combobox
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class LaundryTask:
    name: str
    duration: int
    resource_type: str
    resource_amount: float
    day: str
    
    def __lt__(self, other):
        return self.duration < other.duration

class LaundryScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Laundry Scheduler")
        self.tasks = []
        self.available_slots = []
        self.resources = {'proszek': 5, 'płyn': 3}
        self.days = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
        self.setup_gui()

    def setup_gui(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10)
        
        self.resources_label = tk.Label(self.main_frame, text=self.get_resources_info())
        self.resources_label.pack(pady=5)
        
        self.schedule_text = tk.Text(self.main_frame, height=15, width=50)
        self.schedule_text.pack(pady=10)
        
        buttons = [
            ("Dodaj pranie", self.add_task),
            ("Dodaj slot czasowy", self.add_slot),
            ("Generuj harmonogram", self.generate_schedule),
            ("Uzupełnij zasoby", self.refill_resources),
            ("Usuń pranie", self.remove_task),
            ("Usuń slot", self.remove_slot)
        ]
        
        for text, command in buttons:
            tk.Button(self.main_frame, text=text, command=command).pack(pady=2)

    def time_to_datetime(self, day, time_str):
        try:
            time_obj = datetime.strptime(time_str, "%H:%M")
            return time_obj
        except ValueError:
            return None

    def check_time_overlap(self, start_time, duration, scheduled_times, day):
        end_time = (datetime.strptime(start_time, "%H:%M") + 
                   timedelta(minutes=duration)).strftime("%H:%M")
        
        for scheduled_start, scheduled_duration in scheduled_times.get(day, []):
            scheduled_end = (datetime.strptime(scheduled_start, "%H:%M") + 
                           timedelta(minutes=scheduled_duration)).strftime("%H:%M")
            
            if not (end_time <= scheduled_start or start_time >= scheduled_end):
                return True
        return False

    def get_resources_info(self):
        return f"Dostępne zasoby:\nProszek: {self.resources['proszek']:.2f} kg\nPłyn: {self.resources['płyn']:.2f} l"

    def add_task(self):
        # Utwórz okno dialogowe do dodawania prania
        task_window = tk.Toplevel(self.root)
        task_window.title("Dodaj pranie")
        
        # Wprowadzenie nazwy użytkownika
        tk.Label(task_window, text="Nazwa użytkownika:").pack(pady=5)
        name_entry = tk.Entry(task_window)
        name_entry.pack(pady=5)

        # Wprowadzenie czasu trwania prania
        tk.Label(task_window, text="Czas trwania (minuty):").pack(pady=5)
        duration_entry = tk.Entry(task_window)
        duration_entry.pack(pady=5)

        # Wprowadzenie ilości proszku
        tk.Label(task_window, text="Ilość proszku (kg):").pack(pady=5)
        resource_entry = tk.Entry(task_window)
        resource_entry.pack(pady=5)

        # Dzień tygodnia w rozwijanej liście (Combobox)
        tk.Label(task_window, text="Wybierz dzień tygodnia:").pack(pady=5)
        day_combobox = ttk.Combobox(task_window, values=self.days, state="readonly")
        day_combobox.pack(pady=5)
        
        # Funkcja dodająca pranie
        def add_task_action():
            name = name_entry.get()
            duration = duration_entry.get()
            resource_amount = resource_entry.get()
            day = day_combobox.get()

            try:
                duration = int(duration)
                resource_amount = float(resource_amount)
                
                if not name:
                    messagebox.showerror("Błąd", "Proszę podać nazwę użytkownika!")
                    return
                
                if duration <= 0 or resource_amount <= 0:
                    messagebox.showerror("Błąd", "Czas trwania i ilość proszku muszą być większe od zera!")
                    return
                
                if resource_amount > self.resources['proszek']:
                    messagebox.showerror("Błąd", "Niewystarczająca ilość proszku!")
                    return
                
                if day not in self.days:
                    messagebox.showerror("Błąd", "Proszę wybrać poprawny dzień tygodnia!")
                    return

                task = LaundryTask(name, duration, 'proszek', resource_amount, day)
                self.tasks.append(task)
                self.resources['proszek'] -= resource_amount
                self.update_display()
                task_window.destroy()  # Zamknięcie okna po dodaniu prania

            except ValueError:
                messagebox.showerror("Błąd", "Proszę wprowadzić poprawne wartości dla czasu trwania i ilości proszku!")

        # Przycisk dodający pranie
        tk.Button(task_window, text="Dodaj pranie", command=add_task_action).pack(pady=10)

    def add_slot(self):
        # Utwórz okno dialogowe do dodawania slotu
        slot_window = tk.Toplevel(self.root)
        slot_window.title("Dodaj slot czasowy")
        
        # Dzień tygodnia w rozwijanej liście (Combobox)
        tk.Label(slot_window, text="Wybierz dzień tygodnia:").pack(pady=5)
        day_combobox = ttk.Combobox(slot_window, values=self.days, state="readonly")
        day_combobox.pack(pady=5)
        
        # Godzina (pole tekstowe)
        tk.Label(slot_window, text="Podaj godzinę (HH:MM):").pack(pady=5)
        time_entry = tk.Entry(slot_window)
        time_entry.pack(pady=5)
        
        # Funkcja dodająca slot
        def add_slot_action():
            day = day_combobox.get()
            time = time_entry.get()
            
            if day and time:
                self.available_slots.append((day, time))
                self.update_display()
                slot_window.destroy()  # Zamknięcie okna po dodaniu slotu
            else:
                messagebox.showerror("Błąd", "Proszę wypełnić wszystkie pola!")
        
        # Przycisk dodający slot
        tk.Button(slot_window, text="Dodaj slot", command=add_slot_action).pack(pady=10)

    def generate_schedule(self):
        if not self.tasks or not self.available_slots:
            messagebox.showwarning("Błąd", "Brak zadań lub slotów czasowych!")
            return

        sorted_tasks = sorted(self.tasks, key=lambda x: x.duration)
        schedule = []
        self.scheduled_times = {day: [] for day in self.days}

        for task in sorted_tasks:
            available_day_slots = [slot for slot in self.available_slots 
                                 if slot[0] == task.day]
            
            slot_assigned = False
            for slot in available_day_slots:
                if not self.check_time_overlap(slot[1], task.duration, 
                                             self.scheduled_times, slot[0]):
                    schedule.append(f"{slot[0]} {slot[1]}: {task.name} ({task.duration} min)")
                    self.scheduled_times[slot[0]].append((slot[1], task.duration))
                    slot_assigned = True
                    break
            
            if not slot_assigned:
                messagebox.showwarning("Błąd", 
                    f"Nie można zaplanować prania dla {task.name} - konflikt czasowy!")
                return

        self.schedule_text.delete(1.0, tk.END)
        self.schedule_text.insert(tk.END, "Harmonogram prania:\n\n")
        for entry in schedule:
            self.schedule_text.insert(tk.END, f"{entry}\n")

    def refill_resources(self):
        self.resources['proszek'] = 5
        self.resources['płyn'] = 3
        self.resources_label.config(text=self.get_resources_info())
        messagebox.showinfo("Sukces", "Zasoby zostały uzupełnione!")

    def remove_task(self):
        task_names = [task.name for task in self.tasks]
        name_to_remove = simpledialog.askstring("Usuń pranie", 
                                                 f"Wybierz pranie do usunięcia:\n{', '.join(task_names)}")
        if name_to_remove:
            task_to_remove = next((task for task in self.tasks if task.name == name_to_remove), None)
            if task_to_remove:
                self.tasks.remove(task_to_remove)
                self.resources['proszek'] += task_to_remove.resource_amount
                self.update_display()
            else:
                messagebox.showerror("Błąd", "Nie znaleziono takiego prania!")

    def remove_slot(self):
        available_slots_str = [f"{day} {time}" for day, time in self.available_slots]
        slot_to_remove = simpledialog.askstring("Usuń slot", 
                                                 f"Wybierz slot do usunięcia:\n{', '.join(available_slots_str)}")
        if slot_to_remove:
            day, time = slot_to_remove.split()
            if (day, time) in self.available_slots:
                self.available_slots.remove((day, time))
                self.update_display()
            else:
                messagebox.showerror("Błąd", "Nie znaleziono takiego slotu!")

    def update_display(self):
        self.resources_label.config(text=self.get_resources_info())
        self.schedule_text.delete(1.0, tk.END)
        
        self.schedule_text.insert(tk.END, "Zadania do zaplanowania:\n\n")
        for task in sorted(self.tasks, key=lambda x: x.duration):
            self.schedule_text.insert(tk.END, f"{task.name}: {task.duration} min ({task.day})\n")
        
        self.schedule_text.insert(tk.END, "\nDostępne sloty:\n")
        for day, time in self.available_slots:
            self.schedule_text.insert(tk.END, f"{day} {time}\n")

if __name__ == '__main__':
    root = tk.Tk()
    app = LaundryScheduler(root)
    root.mainloop()
