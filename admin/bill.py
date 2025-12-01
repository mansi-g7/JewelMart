 import tkinter as tk
 from tkinter import ttk
 def open_bill_window(parent, db):
 win = tk.Toplevel(parent)
 win.title('Bills')
 win.geometry('850x420')
 coll = db['bill']
 tree = ttk.Treeview(win,
 columns=('_id','order_id','amount','generated_on'), show='headings')
 for c in ('_id','order_id','amount','generated_on'):
 tree.heading(c, text=c); tree.column(c, width=170)
 tree.pack(fill='both', expand=True, padx=8, pady=8)
 def refresh():
 for r in tree.get_children():
 tree.delete(r)
 for b in coll.find():
 tree.insert('', 'end', values=(str(b.get('_id')),
 str(b.get('order_id','')), b.get('amount',''), b.get('generated_on','')))
 10
tk.Button(win, text='Refresh', command=refresh).pack()
 refresh()