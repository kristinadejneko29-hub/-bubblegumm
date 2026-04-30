import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Файл для хранения данных
        self.data_file = "expenses.json"
        self.expenses = self.load_expenses()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
    
    def load_expenses(self):
        """Загрузка расходов из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_expenses(self):
        """Сохранение расходов в JSON файл"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)
    
    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        # Рамка для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавление расхода", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поле Сумма
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var, width=20)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Поле Категория
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.category_var = tk.StringVar()
        self.categories = ["Еда", "Транспорт", "Развлечения", "Коммунальные услуги", 
                          "Здоровье", "Одежда", "Другое"]
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, 
                                           values=self.categories, width=20)
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.set("Еда")
        
        # Поле Дата
        ttk.Label(input_frame, text="Дата:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.date_entry = DateEntry(input_frame, width=18, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка Добавить
        self.add_btn = ttk.Button(input_frame, text="➕ Добавить расход", command=self.add_expense)
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # Рамка для фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по категории
        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category = tk.StringVar(value="Все")
        all_categories = ["Все"] + self.categories
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category,
                                         values=all_categories, width=20, state="readonly")
        self.filter_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
        
        # Фильтр по дате
        ttk.Label(filter_frame, text="Дата от:").grid(row=0, column=2, padx=5, pady=5)
        self.date_from = DateEntry(filter_frame, width=12, date_pattern='yyyy-mm-dd')
        self.date_from.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Дата до:").grid(row=0, column=4, padx=5, pady=5)
        self.date_to = DateEntry(filter_frame, width=12, date_pattern='yyyy-mm-dd')
        self.date_to.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопки фильтрации
        ttk.Button(filter_frame, text="🔍 Применить фильтр", 
                   command=self.refresh_table).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(filter_frame, text="🗑️ Сбросить фильтр", 
                   command=self.reset_filters).grid(row=0, column=7, padx=5, pady=5)
        
        # Рамка для таблицы
        table_frame = ttk.LabelFrame(self.root, text="Список расходов", padding=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Таблица с прокруткой
        scroll_y = ttk.Scrollbar(table_frame)
        scroll_y.pack(side="right", fill="y")
        
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        scroll_x.pack(side="bottom", fill="x")
        
        self.tree = ttk.Treeview(table_frame, columns=("id", "amount", "category", "date"), 
                                 show="headings", yscrollcommand=scroll_y.set,
                                 xscrollcommand=scroll_x.set)
        
        # Настройка колонок
        self.tree.heading("id", text="ID")
        self.tree.heading("amount", text="Сумма (₽)")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        
        self.tree.column("id", width=50)
        self.tree.column("amount", width=150)
        self.tree.column("category", width=150)
        self.tree.column("date", width=120)
        
        self.tree.pack(fill="both", expand=True)
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        # Рамка для итоговой суммы
        total_frame = ttk.Frame(self.root)
        total_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(total_frame, text="Итоговая сумма за выбранный период:", 
                  font=("Arial", 10, "bold")).pack(side="left", padx=5)
        
        self.total_label = ttk.Label(total_frame, text="0.00 ₽", 
                                     font=("Arial", 12, "bold"), foreground="green")
        self.total_label.pack(side="left", padx=10)
        
        # Кнопка удаления
        delete_btn = ttk.Button(total_frame, text="🗑️ Удалить выбранное", 
                                command=self.delete_expense)
        delete_btn.pack(side="right", padx=5)
        
        # Кнопка обновления
        refresh_btn = ttk.Button(total_frame, text="🔄 Обновить", 
                                 command=self.refresh_table)
        refresh_btn.pack(side="right", padx=5)
    
    def validate_amount(self, amount_str):
        """Проверка корректности суммы"""
        try:
            amount = float(amount_str)
            if amount > 0:
                return True, amount
            else:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                return False, None
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число в поле 'Сумма'!")
            return False, None
    
    def add_expense(self):
        """Добавление нового расхода"""
        amount_str = self.amount_var.get().strip()
        
        if not amount_str:
            messagebox.showerror("Ошибка", "Введите сумму расхода!")
            return
        
        # Проверка суммы
        is_valid, amount = self.validate_amount(amount_str)
        if not is_valid:
            return
        
        category = self.category_var.get()
        date = self.date_entry.get()
        
        # Проверка формата даты
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте YYYY-MM-DD")
            return
        
        # Создание новой записи
        expense_id = len(self.expenses) + 1
        new_expense = {
            "id": expense_id,
            "amount": amount,
            "category": category,
            "date": date
        }
        
        self.expenses.append(new_expense)
        self.save_expenses()
        
        # Очистка поля суммы
        self.amount_var.set("")
        
        # Обновление таблицы
        self.refresh_table()
        
        messagebox.showinfo("Успех", "Расход успешно добавлен!")
    
    def delete_expense(self):
        """Удаление выбранного расхода"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранную запись?"):
            for item in selected:
                values = self.tree.item(item, "values")
                expense_id = int(values[0])
                self.expenses = [e for e in self.expenses if e["id"] != expense_id]
            
            # Перенумерация ID
            for i, expense in enumerate(self.expenses, 1):
                expense["id"] = i
            
            self.save_expenses()
            self.refresh_table()
            messagebox.showinfo("Успех", "Запись удалена!")
    
    def refresh_table(self):
        """Обновление таблицы с учётом фильтров"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение фильтров
        filter_cat = self.filter_category.get()
        date_from = self.date_from.get()
        date_to = self.date_to.get()
        
        # Фильтрация расходов
        filtered_expenses = []
        for expense in self.expenses:
            # Фильтр по категории
            if filter_cat != "Все" and expense["category"] != filter_cat:
                continue
            
            # Фильтр по дате
            expense_date = expense["date"]
            if date_from and expense_date < date_from:
                continue
            if date_to and expense_date > date_to:
                continue
            
            filtered_expenses.append(expense)
        
        # Добавление в таблицу
        for expense in filtered_expenses:
            self.tree.insert("", "end", values=(
                expense["id"],
                f"{expense['amount']:.2f}",
                expense["category"],
                expense["date"]
            ))
        
        # Подсчёт итоговой суммы
        total = sum(expense["amount"] for expense in filtered_expenses)
        self.total_label.config(text=f"{total:.2f} ₽")
    
    def reset_filters(self):
        """Сброс всех фильтров"""
        self.filter_category.set("Все")
        self.date_from.set_date(datetime.now().replace(day=1))
        self.date_to.set_date(datetime.now())
        self.refresh_table()

def main():
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()