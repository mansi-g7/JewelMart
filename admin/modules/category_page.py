import tkinter as tk
from tkinter import ttk, messagebox
from bson import ObjectId




def open_category_window(parent, db):
win = tk.Toplevel(parent)
win.title('Manage Categories')
win.geometry('700x450')


coll = db['category']


frame = tk.Frame(win)
frame.pack(fill='both', expand=True, padx=10, pady=10)


tree = ttk.Treeview(frame, columns=('_id','name'), show='headings')
tree.heading('_id', text='_id'); tree.column('_id', width=220)
tree.heading('name', text='name'); tree.column('name', width=220)
tree.pack(side='left', fill='both', expand=True)


sb = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
tree.configure(yscroll=sb.set)
sb.pack(side='left', fill='y')


form = tk.Frame(win)
form.pack(fill='x', padx=12, pady=8)


tk.Label(form, text='Category Name').grid(row=0, column=0)
name_e = tk.Entry(form, width=40)
name_e.grid(row=0, column=1, padx=8, pady=6)


def refresh():
for r in tree.get_children():
tree.delete(r)
for c in coll.find():
tree.insert('', 'end', values=(str(c.get('_id')), c.get('name','')))


def add():
if not name_e.get().strip():
messagebox.showwarning('Input', 'Enter category name')
return
coll.insert_one({'name': name_e.get().strip()})
name_e.delete(0,'end')
refresh()


def delete():
sel = tree.focus()
if not sel:
messagebox.showwarning('Select', 'Select category')
return
oid = ObjectId(tree.item(sel,'values')[0])
coll.delete_one({'_id': oid})
refresh()


tk.Button(form, text='Add', command=add, bg='green', fg='white').grid(row=1, column=0, pady=10)
tk.Button(form, text='Delete', command=delete, bg='red', fg='white').grid(row=1, column=1, pady=10)


refresh()