 import tkinter as tk
 from tkinter import ttk, messagebox
 from bson import ObjectId
 def open_jewel_window(parent, db):
 win = tk.Toplevel(parent)
 win.title('Manage Jewellery (jewel_add)')
 win.geometry('1000x520')
 coll = db['jewel_add']
 frame = tk.Frame(win)
 frame.pack(fill='both', expand=True, padx=10, pady=10)
 cols = ('_id','name','category','price','weight','description')
 tree = ttk.Treeview(frame, columns=cols, show='headings')
 for c in cols:
 tree.heading(c, text=c); tree.column(c, width=150)
 tree.pack(side='left', fill='both', expand=True)
 sb = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
 tree.configure(yscroll=sb.set)
 sb.pack(side='left', fill='y')
 form = tk.Frame(win)
 form.pack(fill='x', padx=12, pady=8)
 tk.Label(form, text='Name').grid(row=0, column=0)
 name_e = tk.Entry(form, width=30); name_e.grid(row=0, column=1)
 tk.Label(form, text='Category').grid(row=1, column=0)
 cat_e = tk.Entry(form, width=30); cat_e.grid(row=1, column=1)
 tk.Label(form, text='Price').grid(row=2, column=0)
 price_e = tk.Entry(form, width=30); price_e.grid(row=2, column=1)
 tk.Label(form, text='Weight').grid(row=3, column=0)
 weight_e = tk.Entry(form, width=30); weight_e.grid(row=3, column=1)
 tk.Label(form, text='Description').grid(row=4, column=0)
 desc_e = tk.Entry(form, width=60); desc_e.grid(row=4, column=1,
 columnspan=3)
 def refresh():
 for r in tree.get_children():
 tree.delete(r)
 for p in coll.find():
 6
tree.insert('', 'end', values=(str(p.get('_id')),
 p.get('name',''), p.get('category',''), p.get('price',''),
 p.get('weight',''), p.get('description','')))
 def add():
 try:
 price_val = float(price_e.get()) if price_e.get() else 0.0
 except:
 messagebox.showerror('Error','Price must be numeric')
 return
 coll.insert_one({
 'name': name_e.get().strip(),
 'category': cat_e.get().strip(),
 'price': price_val,
 'weight': weight_e.get().strip(),
 'description': desc_e.get().strip()
 })
 name_e.delete(0,'end'); cat_e.delete(0,'end');
 price_e.delete(0,'end'); weight_e.delete(0,'end'); desc_e.delete(0,'end')
 refresh()
 def update():
 sel = tree.focus()
 if not sel:
 messagebox.showwarning('Select','Select product')
 return
 vals = tree.item(sel,'values')
 oid = ObjectId(vals[0])
 try:
 price_val = float(price_e.get()) if price_e.get() else 0.0
 except:
 messagebox.showerror('Error','Price must be numeric')
 return
 coll.update_one({'_id': oid}, {'$set': {
 'name': name_e.get().strip(),
 'category': cat_e.get().strip(),
 'price': price_val,
 'weight': weight_e.get().strip(),
 'description': desc_e.get().strip()
 }})
 refresh()
 def delete():
 sel = tree.focus()
 if not sel:
 messagebox.showwarning('Select','Select product')
 return
 oid = ObjectId(tree.item(sel,'values')[0])
 coll.delete_one({'_id': oid})
 refresh()
 7
def on_select(event):
 sel = tree.focus()
 if not sel:
 return
 vals = tree.item(sel,'values')
 name_e.delete(0,'end'); name_e.insert(0, vals[1])
 cat_e.delete(0,'end'); cat_e.insert(0, vals[2])
 price_e.delete(0,'end'); price_e.insert(0, vals[3])
 weight_e.delete(0,'end'); weight_e.insert(0, vals[4])
 desc_e.delete(0,'end'); desc_e.insert(0, vals[5])
 tree.bind('<<TreeviewSelect>>', on_select)
 tk.Button(form, text='Add', command=add, bg='green',
 fg='white').grid(row=5, column=0, pady=10)
 tk.Button(form, text='Update', command=update, bg='blue',
 fg='white').grid(row=5, column=1, pady=10)
 tk.Button(form, text='Delete', command=delete, bg='red',
 fg='white').grid(row=5, column=2, pady=10)
 refresh()