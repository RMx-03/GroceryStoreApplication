# Grocery Store Application - Feature Implementation Guide

This guide outlines the steps to transform the current read-only application into a fully functional CRUD (Create, Read, Delete) application.

## Overview
We will implement the following features:
1.  **Units of Measure (UOM) Support**: Allow the frontend to fetch available units (like kg, pcs) for the "Add Product" form.
2.  **Delete Product**: Enable removing products from the database.
3.  **Add Product**: Enable adding new products with a name, unit, and price.

---

## Part 1: Backend Implementation

### Step 1: Update `products_dao.py`
**Goal**: Add a function to fetch Units of Measure (UOM) from the database. The frontend needs this list for the dropdown menu when adding a new product.

**Action**: Open `backend/products_dao.py` and add the `get_uoms` function.

```python
# Add this function to backend/products_dao.py

def get_uoms(connection):
    cursor = connection.cursor()
    query = ("SELECT * FROM uom")
    cursor.execute(query)
    response = []
    for (uom_id, uom_name) in cursor:
        response.append({
            'uom_id': uom_id,
            'uom_name': uom_name
        })
    return response
```

### Step 2: Update `server.py`
**Goal**: Expose the new capabilities (Get UOMs, Delete Product, Insert Product) as HTTP endpoints. We also need to ensure Cross-Origin Resource Sharing (CORS) is handled so the React app (port 5173) can talk to Flask (port 5000).

**Action**: Open `backend/server.py` and update it with the following code. Note the standard usage of a CORS decorator or library is recommended for production, but we will stick to the manual header injection matching your current style, while adding robustness for POST requests.

```python
from flask import Flask, request, jsonify
from sql_connection import get_sql_connection
import products_dao

app = Flask(__name__)

connection = get_sql_connection()

# --- Helper for CORS ---
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/getUOM', methods=['GET'])
def get_uom():
    response = products_dao.get_uoms(connection)
    response = jsonify(response)
    return add_cors_headers(response)

@app.route('/getProducts', methods=['GET'])
def get_products():
    products = products_dao.get_all_products(connection)
    response = jsonify(products)
    return add_cors_headers(response)

@app.route('/insertProduct', methods=['POST'])
def insert_product():
    request_payload = request.get_json()
    product_id = products_dao.insert_new_product(connection, request_payload)
    response = jsonify({
        'product_id': product_id
    })
    return add_cors_headers(response)

@app.route('/deleteProduct', methods=['POST'])
def delete_product():
    request_payload = request.get_json()
    product_id = request_payload['product_id']
    products_dao.delete_product(connection, product_id)
    response = jsonify({
        'product_id': product_id
    })
    return add_cors_headers(response)

# Handle preflight requests for POST/DELETE
@app.after_request
def after_request(response):
    return add_cors_headers(response)

if __name__ == "__main__":
    print("Starting Python Flask Server For Grocery Store Management System")
    app.run(port=5000)
```

---

## Part 2: Frontend Implementation

### Step 3: Update Types and State in `App.tsx`
**Goal**: Define the data structures for UOMs and the New Product form, and add state variables to hold this data.

**Action**: Update `ui/src/App.tsx`.

1.  **Define Interfaces**:
    Add the `UOM` interface alongside `Product`.

    ```typescript
    interface UOM {
      uom_id: number;
      uom_name: string;
    }
    
    // Existing Product interface...
    interface Product {
      product_id: number;
      name: string;
      uom_id: number;
      price_per_unit: number;
      uom_name: string;
    }
    ```

2.  **Add State**:
    Inside the `App` component, add state for UOMs and the new product form inputs.

    ```typescript
    // Inside App function...
    const [uoms, setUoms] = useState<UOM[]>([]);
    const [newProduct, setNewProduct] = useState({
      name: '',
      uom_id: 0, // Default to 0 or first available ID
      price_per_unit: 0
    });
    ```

### Step 4: Implement Fetching and Action Functions
**Goal**: Create functions to load UOMs on startup, handle form changes, submit new products, and delete existing ones.

**Action**: Add these functions inside `App.tsx`.

```typescript
  // Fetch UOMs on load
  useEffect(() => {
    fetch('http://127.0.0.1:5000/getUOM')
      .then(response => response.json())
      .then(data => setUoms(data))
      .catch(error => console.error('Error fetching UOMs:', error));
  }, []);

  // Helper to refresh products
  const loadProducts = () => {
    setLoading(true);
    fetch('http://127.0.0.1:5000/getProducts')
      .then(response => response.json())
      .then(data => {
        setProducts(data);
        setLoading(false);
      });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setNewProduct(prev => ({
      ...prev,
      [name]: name === 'price_per_unit' || name === 'uom_id' ? parseFloat(value) : value
    }));
  };

  const handleAddProduct = () => {
    fetch('http://127.0.0.1:5000/insertProduct', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newProduct)
    })
    .then(response => response.json())
    .then(() => {
        loadProducts(); // Refresh list
        setNewProduct({ name: '', uom_id: uoms[0]?.uom_id || 0, price_per_unit: 0 }); // Reset form
    })
    .catch(error => console.error('Error adding product:', error));
  };

  const handleDeleteProduct = (productId: number) => {
    fetch('http://127.0.0.1:5000/deleteProduct', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: productId })
    })
    .then(response => response.json())
    .then(() => {
        loadProducts(); // Refresh list
    })
    .catch(error => console.error('Error deleting product:', error));
  };
```

### Step 5: Update the UI Render
**Goal**: Add the "Add Product" form and the "Delete" button column to the table.

**Action**: Update the return statement in `App.tsx`.

```tsx
return (
  <div className="container">
    <h1>Grocery Store Products</h1>
    
    {/* Add Product Section */}
    <div className="card add-product-form">
      <h2>Add New Product</h2>
      <div className="form-group">
        <input 
          type="text" 
          name="name" 
          placeholder="Product Name" 
          value={newProduct.name} 
          onChange={handleInputChange} 
        />
        <select name="uom_id" value={newProduct.uom_id} onChange={handleInputChange}>
            <option value={0} disabled>Select Unit</option>
            {uoms.map(uom => (
                <option key={uom.uom_id} value={uom.uom_id}>{uom.uom_name}</option>
            ))}
        </select>
        <input 
          type="number" 
          name="price_per_unit" 
          placeholder="Price" 
          value={newProduct.price_per_unit} 
          onChange={handleInputChange} 
        />
        <button onClick={handleAddProduct}>Add Product</button>
      </div>
    </div>

    {/* Product List Section */}
    <div className="card">
      {loading ? (
         <p>Loading products...</p>
      ) : products.length > 0 ? (
        <table className="product-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Unit</th>
              <th>Price / Unit</th>
              <th>Action</th> {/* New Column */}
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product.product_id}>
                <td>{product.product_id}</td>
                <td>{product.name}</td>
                <td>{product.uom_name}</td>
                <td>${product.price_per_unit}</td>
                <td>
                    <button 
                        className="delete-btn"
                        onClick={() => handleDeleteProduct(product.product_id)}
                    >
                        Delete
                    </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No products found or backend not running.</p>
      )}
    </div>
  </div>
)
```

### Step 6: Basic Styling (Optional)
**Goal**: Make the form look decent.

**Action**: Add this to `ui/src/App.css`.

```css
.add-product-form {
  margin-bottom: 2rem;
  border-bottom: 1px solid #444;
  padding-bottom: 2rem;
}

.form-group {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.form-group input, .form-group select {
  padding: 0.6em;
  border-radius: 8px;
  border: 1px solid #555;
  background-color: #333;
  color: white;
}

.delete-btn {
  background-color: #ff4444;
  color: white;
  padding: 0.4em 0.8em;
  font-size: 0.9em;
}

.delete-btn:hover {
  background-color: #cc0000;
  border-color: #cc0000;
}
```
