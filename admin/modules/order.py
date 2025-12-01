 import tkinter as tk
 from tkinter import ttk, messagebox
 from bson import ObjectId
 def open_order_window(parent, db):
 win = tk.Toplevel(parent)
 win.title('Orders')
 win.geometry('1000x500')
 coll = db['order']
 cols = ('_id','user_id','items','status','total','order_date')
 tree = ttk.Treeview(win, columns=cols, show='headings')
 for c in cols:
 tree.heading(c, text=c); tree.column(c, width=150)
 tree.pack(fill='both', expand=True, padx=8, pady=8)
 def refresh():
 for r in tree.get_children():
 tree.delete(r)
 for o in coll.find():
 tree.insert('', 'end', values=(str(o.get('_id')),
 str(o.get('user_id','')), str(o.get('items',[])), o.get('status',''),
 o.get('total',''), o.get('order_date','')))
 tk.Button(win, text='Refresh', command=refresh).pack()
 refresh(