import { useEffect, useState } from 'react'
import './App.css'

interface Product {
  product_id: number;
  name: string;
  uom_id: number;
  price_per_unit: number;
  uom_name: string;
}

function App() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/getProducts')
      .then(response => response.json())
      .then(data => {
        setProducts(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching products:', error);
        setLoading(false);
      });
  }, [])

  return (
    <div className="container">
      <h1>Grocery Store Products</h1>
      <div className="card">
        {loading ? (
           <p>Loading products...</p>
        ) : products.length > 0 ? (
          <table className="product-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Unit (UOM)</th>
                <th>Price / Unit</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => (
                <tr key={product.product_id}>
                  <td>{product.product_id}</td>
                  <td>{product.name}</td>
                  <td>{product.uom_name}</td>
                  <td>${product.price_per_unit}</td>
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
}

export default App