 import tkinter as tk
 from tkinter import ttk, messagebox
 from bson import ObjectId
 def open_register_window(parent, db):
 win = tk.Toplevel(parent)
 win.title('Registered Users')
 win.geometry('900x450')
 11
coll = db['register']
 tree = ttk.Treeview(win,
 columns=('_id','username','password','email','mobile'), show='headings')
 for c in ('_id','username','password','email','mobile'):
 tree.heading(c, text=c); tree.column(c, width=160)
 tree.pack(fill='both', expand=True, padx=8, pady=8)
 def refresh():
 for r in tree.get_children():
 tree.delete(r)
 for u in coll.find():
 tree.insert('', 'end', values=(str(u.get('_id')),
 u.get('username',''), u.get('password',''), u.get('email',''),
 u.get('mobile','')))
 def delete():
 sel = tree.focus()
 if not sel:
 messagebox.showwarning('Select', 'Select user')
 return
 oid = ObjectId(tree.item(sel,'values')[0])
 coll.delete_one({'_id': oid})
 refresh()
 tk.Button(win, text='Refresh', command=refresh).pack(side='left', padx=8,
 pady=6)
 tk.Button(win, text='Delete User', command=delete, bg='red',
 fg='white').pack(side='left', padx=6)
 refresh()