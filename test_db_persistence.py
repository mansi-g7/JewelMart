"""
Test script to verify database persistence between admin and user panels
This script will:
1. Connect to MongoDB
2. Add a test product to the jewel_add collection
3. Verify it was inserted
4. Delete the test product
5. Verify it was deleted
"""

import sys
import os
from pymongo import MongoClient
from datetime import datetime

# Add admin folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'admin'))

from database import get_products_collection

def test_product_insert():
    """Test inserting a product"""
    print("\n" + "="*60)
    print("TEST 1: PRODUCT INSERT")
    print("="*60)
    
    products_coll = get_products_collection()
    
    # Get the last ID
    last = products_coll.find_one(sort=[("id", -1)])
    next_id = (last.get("id", 0) if last else 0) + 1
    
    # Create test product
    test_doc = {
        "id": next_id,
        "name": f"TEST_PRODUCT_{datetime.now().strftime('%H%M%S')}",
        "price": 99.99,
        "category": "Test",
        "image_path": "test.jpg",
        "description": "This is a test product"
    }
    
    print(f"Inserting test product: {test_doc}")
    
    try:
        result = products_coll.insert_one(test_doc)
        print(f"✓ Successfully inserted with ID: {result.inserted_id}")
        
        # Verify it exists
        found = products_coll.find_one({"id": next_id})
        if found:
            print(f"✓ Successfully retrieved from database: {found['name']}")
            return test_doc
        else:
            print(f"✗ ERROR: Product was not found in database after insertion!")
            return None
            
    except Exception as e:
        print(f"✗ ERROR inserting product: {e}")
        return None

def test_product_delete(test_doc):
    """Test deleting a product"""
    print("\n" + "="*60)
    print("TEST 2: PRODUCT DELETE")
    print("="*60)
    
    products_coll = get_products_collection()
    
    test_id = test_doc["id"]
    print(f"Deleting product with ID: {test_id} (Name: {test_doc['name']})")
    
    try:
        result = products_coll.delete_one({"id": test_id})
        print(f"✓ Delete operation completed. Deleted count: {result.deleted_count}")
        
        # Verify it's gone
        found = products_coll.find_one({"id": test_id})
        if found:
            print(f"✗ ERROR: Product still exists after deletion!")
            return False
        else:
            print(f"✓ Confirmed: Product successfully removed from database")
            return True
            
    except Exception as e:
        print(f"✗ ERROR deleting product: {e}")
        return False

def test_read_all_products():
    """Test reading all products"""
    print("\n" + "="*60)
    print("TEST 3: READ ALL PRODUCTS")
    print("="*60)
    
    products_coll = get_products_collection()
    
    try:
        docs = list(products_coll.find())
        print(f"✓ Successfully read {len(docs)} products from database")
        
        if len(docs) > 0:
            print("\nFirst 3 products:")
            for doc in docs[:3]:
                print(f"  - ID: {doc.get('id')}, Name: {doc.get('name')}")
        
        return True
        
    except Exception as e:
        print(f"✗ ERROR reading products: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("JEWELMART DATABASE PERSISTENCE TEST")
    print("="*60)
    
    # Test 1: Read all products
    test_read_all_products()
    
    # Test 2: Insert a product
    test_doc = test_product_insert()
    
    if test_doc:
        # Test 3: Delete the product
        test_product_delete(test_doc)
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
