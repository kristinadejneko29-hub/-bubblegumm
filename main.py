import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("950x600")
        
        # Файл для данных
        self.data_file = "expenses.json"
        self.expenses = self.load_expenses()
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Показываем данные
        self.refresh_table()
    
    def load_expenses(self):
        """Загрузка из JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_expenses(self):
        """Сохранение в JSON"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)
    
    def create_widgets(self):
        """Создание всех виджетов"""
        # ========== ВЕРХНЯЯ ЧАСТЬ - ДОБАВЛЕНИЕ ==========
        add_frame = tk.LabelFrame(self.root, text="➕ Добавление расхода", font=("Arial", 10, "bold"))
        add_frame.pack(fill="x", padx=10, pady=5, ipady=5)
        
        # Строка 1
        row1 = tk.Frame(add_frame)
        row1.pack(fill="x", padx=5, pady=5)
        
        tk.Label(row1, text="Сумма:", width=10, anchor="w").pack(side="left", padx=5)
        self.amount_entry = tk.Entry(row1, width=20)
        self.amount_entry.pack(side="left", padx=5)
        
        tk.Label(row1, text="Категория:", width=10, anchor="w").pack(side="left", padx=5)
        self.category_var = tk.StringVar(value="Еда")
        categories = ["Еда", "Транспорт", "Развлечения", "Коммунальные", "Здоровье", "Одежда", "Другое"]
        self.category_combo = ttk.Combobox(row1, textvariable=self.category_var, values=categories, width=15)
        self.category_combo.pack(side="left", padx=5)
        
        tk.Label(row1, text="Дата (ГГГГ-ММ-ДД):", width=15, anchor="w").pack(side="left", padx=5)
        self.date_entry = tk.Entry(row1, width=15)
        self.date_entry.pack(side="left", padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        self.add_btn = tk.Button(row1, text="Добавить", bg="green", fg="white", 
                                  font=("Arial", 9, "bold"), command=self.add_expense)
        self.add_btn.pack(side="left", padx=20)
        
        # ========== СРЕДНЯЯ ЧАСТЬ - ФИЛЬТРЫ ==========
        filter_frame = tk.LabelFrame(self.root, text="🔍 Фильтрация", font=("Arial", 10, "bold"))
        filter_frame.pack(fill="x", padx=10, pady=5, ipady=5)
        
        row2 = tk.Frame(filter_frame)
        row2.pack(fill="x", padx=5, pady=5)
        
        tk.Label(row2, text="Категория:").pack(side="left", padx=5)
        self.filter_category = tk.StringVar(value="Все")
        filter_cats = ["Все"] + ["Еда", "Транспорт", "Развлечения", "Коммунальные", "Здоровье", "Одежда", "Другое"]
        self.filter_combo = ttk.Combobox(row2, textvariable=self.filter_category, values=filter_cats, width=15, state="readonly")
        self.filter_combo.pack(side="left", padx=5)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
        
        tk.Label(row2, text="Дата от:").pack(side="left", padx=5)
        self.date_from = tk.Entry(row2, width=12)
        self.date_from.pack(side="left", padx=5)
        self.date_from.insert(0, "2024-01-01")
        
        tk.Label(row2, text="Дата до:").pack(side="left", padx=5)
        self.date_to = tk.Entry(row2, width=12)
        self.date_to.pack(side="left", padx=5)
        self.date_to.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        tk.Button(row2, text="Применить фильтр", bg="blue", fg="white", 
                  command=self.refresh_table).pack(side="left", padx=10)
        tk.Button(row2, text="Сбросить фильтр", bg="orange", fg="white", 
                  command=self.reset_filters).pack(side="left", padx=5)
        
        # ========== ТАБЛИЦА ==========
        table_frame = tk.LabelFrame(self.root, text="📋 Список расходов", font=("Arial", 10, "bold"))
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Прокрутка
        scroll_y = tk.Scrollbar(table_frame)
        scroll_y.pack(side="right", fill="y")
        
        scroll_x = tk.Scrollbar(table_frame, orient="horizontal")
        scroll_x.pack(side="bottom", fill="x")
        
        # Таблица
        columns = ("id", "amount", "category", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                  yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("amount", text="Сумма (₽)")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("amount", width=150, anchor="center")
        self.tree.column("category", width=150, anchor="center")
        self.tree.column("date", width=120, anchor="center")
        
        self.tree.pack(fill="both", expand=True)
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        # ========== НИЖНЯЯ ЧАСТЬ - ИТОГО ==========
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="x", padx=10, pady=5)
        
        self.total_label = tk.Label(bottom_frame, text="Общая сумма: 0.00 ₽", 
                                     font=("Arial", 12, "bold"), fg="green")
        self.total_label.pack(side="left", padx=10)
        
        tk.Button(bottom_frame, text="Удалить выбранное", bg="red", fg="white",
                  command=self.delete_expense).pack(side="right", padx=5)
        
        tk.Button(bottom_frame, text="Обновить", bg="gray", fg="white",
                  command=self.refresh_table).pack(side="right", padx=5)
    
    def add_expense(self):
        """Добавление расхода"""
        # Получаем сумму
        amount_str = self.amount_entry.get().strip()
        if not amount_str:
            messagebox.showerror("Ошибка", "Введите сумму!")
            return
        
        # Проверяем сумму
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть больше 0!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть числом!")
            return
        
        # Получаем категорию
        category = self.category_var.get()
        
        # Получаем и проверяем дату
        date = self.date_entry.get().strip()
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД (например, 2024-01-15)")
            return
        
        # Добавляем расход
        new_id = len(self.expenses) + 1
        self.expenses.append({
            "id": new_id,
            "amount": amount,
            "category": category,
            "date": date
        })
        
        self.save_expenses()
        self.amount_entry.delete(0, tk.END)
        self.refresh_table()
        messagebox.showinfo("Успех", "Расход добавлен!")
    
    def delete_expense(self):
        """Удаление выбранного расхода"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранные записи?"):
            # Получаем ID для удаления
            ids_to_delete = []
            for item in selected:
                values = self.tree.item(item, "values")
                ids_to_delete.append(int(values[0]))
            
            # Удаляем
            self.expenses = [e for e in self.expenses if e["id"] not in ids_to_delete]
            
            # Перенумеровываем ID
            for i, expense in enumerate(self.expenses, 1):
                expense["id"] = i
            
            self.save_expenses()
            self.refresh_table()
            messagebox.showinfo("Успех", "Записи удалены!")
    
    def refresh_table(self):
        """Обновление таблицы с фильтрацией"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получаем фильтры
        filter_cat = self.filter_category.get()
        date_from = self.date_from.get().strip()
        date_to = self.date_to.get().strip()
        
        # Фильтруем
        filtered = []
        for exp in self.expenses:
            # Фильтр по категории
            if filter_cat != "Все" and exp["category"] != filter_cat:
                continue
            
            # Фильтр по дате
            if date_from and exp["date"] < date_from:
                continue
            if date_to and exp["date"] > date_to:
                continue
            
            filtered.append(exp)
        
        # Добавляем в таблицу
        for exp in filtered:
            self.tree.insert("", "end", values=(
                exp["id"],
                f"{exp['amount']:.2f}",
                exp["category"],
                exp["date"]
            ))
        
        # Считаем итого
        total = sum(exp["amount"] for exp in filtered)
        self.total_label.config(text=f"Общая сумма: {total:.2f} ₽")
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.filter_category.set("Все")
        self.date_from.delete(0, tk.END)
        self.date_from.insert(0, "2024-01-01")
        self.date_to.delete(0, tk.END)
        self.date_to.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.refresh_table()

# Запуск
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()