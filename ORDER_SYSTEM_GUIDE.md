# JewelMart Order Management System

## Overview
A complete e-commerce order management system with Amazon/Flipkart-like functionality integrated into JewelMart.

## Features Implemented

### 1. **Order Page (order_page.py)**
Amazon/Flipkart-style order management with:

#### Order Listing
- **All Orders Tab**: View all orders
- **Pending Tab**: Orders being processed
- **Shipped Tab**: Orders in transit
- **Delivered Tab**: Completed orders

#### Order Cards Display
- Order ID and date
- Status badge with color coding
- Items summary (count and quantity)
- Item preview (first 3 items)
- Total amount
- "View Details" button

#### Order Details Dialog
- Complete order information
- **Order Tracking Timeline**:
  - Order Placed ✓
  - Processing ✓
  - Shipped ✓
  - Out for Delivery ✓
  - Delivered ✓
- Items table with quantities
- Price breakdown:
  - Items total
  - Delivery charges (FREE)
  - Total amount
- Delivery address display

### 2. **Enhanced Cart System (cart.py)**

#### Shopping Cart Features
- MongoDB persistence per user
- Add/remove items
- Update quantities
- Real-time total calculation
- Item count tracking

#### Delivery Address Dialog
- Full name
- Phone number (10 digits)
- Complete address
- City, State, PIN code
- Form validation

#### Checkout Process
1. View cart items
2. Edit quantities
3. Enter delivery address
4. Confirm order
5. Order saved to database
6. Cart cleared automatically

### 3. **User Panel Integration (user_panel.py)**

#### New Buttons Added
- **📦 My Orders**: Opens order page
- **👤 Login**: Opens login/registration
- **🛒 View Cart**: Opens shopping cart

#### Navigation Flow
```
User Panel → Add to Cart → View Cart → Checkout → Enter Address → Confirm → My Orders
```

## Database Structure

### Collections Used

#### 1. **carts** Collection
```javascript
{
  user_id: "guest" or email,
  items: [
    {
      id: "product_id",
      name: "Product Name",
      price: 1000,
      qty: 2
    }
  ],
  last_updated: ISODate(),
  total: 2000,
  item_count: 2
}
```

#### 2. **order** Collection
```javascript
{
  order_id: "A1B2C3D4",
  user_id: "guest" or email,
  items: [
    {
      id: "product_id",
      name: "Product Name",
      price: 1000,
      qty: 2
    }
  ],
  total: 2000,
  status: "pending", // pending, processing, shipped, out_for_delivery, delivered
  delivery_address: "Full address string",
  created_at: ISODate()
}
```

#### 3. **register** Collection (Users)
```javascript
{
  username: "Full Name",
  email: "user@example.com",
  password: "hashed_password",
  mobile: "1234567890",
  gender: "Male/Female/Other",
  address: "User address",
  created_at: ISODate()
}
```

## How to Use

### For Customers

1. **Browse Products**
   - View products by category
   - Search for products
   - View product details

2. **Add to Cart**
   - Click "Add to Cart" on product cards
   - Select quantity in product details
   - Items saved to database

3. **View Cart**
   - Click "🛒 View Cart" button
   - Edit quantities
   - Remove items
   - See total amount

4. **Checkout**
   - Click "Proceed to Checkout"
   - Enter delivery address
   - Confirm order
   - Receive order ID

5. **Track Orders**
   - Click "📦 My Orders" button
   - View all orders
   - Filter by status
   - Click "View Details" for tracking

### For Admin

Orders placed by users appear in:
- Admin Panel → Orders section
- Database: `JewelMart.order` collection

Admin can:
- View all orders
- Update order status
- Manage deliveries

## Status Flow

```
pending → processing → shipped → out_for_delivery → delivered
```

## Color Coding

- **Pending**: Orange (#FF9800)
- **Processing**: Blue (#2196F3)
- **Shipped**: Purple (#9C27B0)
- **Out for Delivery**: Red-Orange (#FF5722)
- **Delivered**: Green (#4CAF50)
- **Cancelled**: Red (#F44336)

## Key Files

1. **order_page.py** - Order management UI
2. **cart.py** - Shopping cart and checkout
3. **user_panel.py** - Main user interface
4. **login_registration.py** - User authentication
5. **admin/database.py** - Database connections

## Testing

### Test Order Flow
1. Run `python user_panel.py`
2. Add products to cart
3. Click "View Cart"
4. Click "Proceed to Checkout"
5. Enter delivery address
6. Confirm order
7. Click "My Orders" to view

### Test Order Page Standalone
```bash
python order_page.py
```

## Integration with Admin Panel

- All user registrations sync with admin panel
- Orders visible in admin order management
- Shared MongoDB database: `JewelMart`
- Collections: `register`, `order`, `carts`, `jewel_add`

## Future Enhancements

- Payment gateway integration
- Order cancellation
- Return/refund management
- Email notifications
- SMS alerts
- Invoice generation
- Order rating and reviews
- Wishlist functionality

## Notes

- User ID defaults to "guest" if not logged in
- Cart persists across sessions
- Orders are permanent records
- Delivery is marked as FREE
- Order IDs are 8-character unique codes
