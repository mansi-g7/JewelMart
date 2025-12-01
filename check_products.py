from admin.database import get_products_collection

docs = list(get_products_collection().find())
print(f'Total products: {len(docs)}')
for d in docs:
    print(f'  ID {d.get("id")}: {d.get("name")}')
