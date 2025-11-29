import tkinter as tk
 from tkinter import ttk
 def open_payment_window(parent, db):
 win = tk.Toplevel(parent)
 win.title('Payments')
 win.geometry('850x420')
 9
coll = db['payment']
 tree = ttk.Treeview(win,
 columns=('_id','order_id','amount','method','status','paid_on'),
 show='headings')
 for c in ('_id','order_id','amount','method','status','paid_on'):
 tree.heading(c, text=c); tree.column(c, width=140)
 tree.pack(fill='both', expand=True, padx=8, pady=8)
 def refresh():
 for r in tree.get_children():
 tree.delete(r)
 for p in coll.find():
 tree.insert('', 'end', values=(str(p.get('_id')),
 str(p.get('order_id','')), p.get('amount',''), p.get('method',''),
 p.get('status',''), p.get('paid_on','')))
 tk.Button(win, text='Refresh', command=refresh).pack()
 refresh()