import { useState } from "react";
import { useEffect } from "react";
import { Link } from "react-router";

function ProductsPage() {
    const[products, setProducts] = useState([]);
 
    useEffect(() => {
        async function loadProducts() {
            const res = await fetch("https://dummyjson.com/products");
            const data = await res.json();
            
            setProducts(data.products);
        }
        loadProducts();
    }, []);

    return(
        <>
        <p>Loaded {products.length} products</p>
        <ul>
            {products.map((product) => (
                <li key={product.id}>
                    <img src={product.thumbnail}></img>
                    <h3>Title - {product.title}</h3>
                    <p>Price - ${product.price}</p>
                    <p>Ratings - {product.rating}</p>
                    <p>Category - {product.category}</p>
                    <p>no.of Reviews - {product.reviews.length}</p>
                    <Link to={`/products/${product.id}`}>View Details</Link>

                
                </li>

            ))}
        </ul>
        </>
    )

}

export default ProductsPage;