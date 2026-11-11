import {useState, useEffect} from "react";
import {Link} from "react-router";

function BrowserPage() {
    const[products, setProducts] = useState([]);
    const[page, setPage] = useState(1);

    useEffect(() => {
        async function loadProducts() {
            const skip = (page - 1) * 10;
            const res = await fetch(`https://dummyjson.com/products?limit=10&skip=${skip}`);
            const data = await res.json();
            setProducts(data.products);
        }
        loadProducts();
    }, [page]);

    return (
        <>
        <button disabled={page === 1} onClick={() => setPage(page - 1)}> Previous </button>
        <span> Page {page} </span>
        <button onClick={() => setPage(page + 1)}> Next </button>
        <p>Loaded {products.length} products</p>
        <ul>
            {products.map((product) => (
                <li key={product.id}>
                    <img src={product.thumbnail}></img>
                    <h3>Title - {product.title}</h3>
                    <p>Price - ${product.price}</p>
                    <p>Ratings - {product.rating}</p>
                    <p>Category - {product.category}</p>
                    <Link to={`/products/${product.id}`}>View Details</Link>
        
                </li>

            ))}
        </ul>
        </>
    );
}

export default BrowserPage;