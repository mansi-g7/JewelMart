import tkinter as tk
 from tkinter import ttk
 def open_review_window(parent, db):
 win = tk.Toplevel(parent)
 win.title('Reviews')
 win.geometry('900x450')
 coll = db['review']
 tree = ttk.Treeview(win,
 columns=('_id','user_id','product_id','rating','comment','created_on'),
 show='headings')
 for c in ('_id','user_id','product_id','rating','comment','created_on'):
 tree.heading(c, text=c); tree.column(c, width=140)
 tree.pack(fill='both', expand=True, padx=8, pady=8)
 def refresh():
 for r in tree.get_children():
 tree.delete(r)
 for rv in coll.find():
 tree.insert('', 'end', values=(str(rv.get('_id')),
 str(rv.get('user_id','')), str(rv.get('product_id','')), rv.get('rating',''),
 rv.get('comment',''), rv.get('created_on','')))
 tk.Button(win, text='Refresh', command=refresh).pack()
 refresh()
