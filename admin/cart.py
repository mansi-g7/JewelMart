 import tkinter as tk
 from tkinter import ttk, messagebox
 from bson import ObjectId
 def open_cart_window(parent, db):
 win = tk.Toplevel(parent)
 win.title('Carts')
 win.geometry('900x450')
 coll = db['cart']
 tree = ttk.Treeview(win, columns=('_id','user_id','items','total'),
 show='headings')
 for c in ('_id','user_id','items','total'):
 tree.heading(c, text=c); tree.column(c, width=200)
 tree.pack(fill='both', expand=True, padx=8, pady=8)
 def refresh():
 for r in tree.get_children():
 tree.delete(r)
 for c in coll.find():
 tree.insert('', 'end', values=(str(c.get('_id')),
 str(c.get('user_id','')), str(c.get('items',[])), c.get('total','')))
 8
tk.Button(win, text='Refresh', command=refresh).pack(pady=6)
 refresh()