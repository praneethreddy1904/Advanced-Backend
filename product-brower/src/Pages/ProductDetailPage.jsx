import {useState, useEffect} from "react";
import {useParams} from "react-router";
import {Link} from "react-router";

function ProductDetailPage() {
    const {id} = useParams();
    const[products, setProducts] = useState([]);

    useEffect(() => {
        async function loadProducts() {
            const res = await fetch(`https://dummyjson.com/products/${id}`);
            const data = await res.json();
            
            setProducts(data);
        }
        loadProducts();
    }, [id]);

    if (!products) {
        return <p>Loading...</p>
    }

    return(
        <>
            <Link to={`/products/${id}`}>Back to Product List</Link>
            <h2>Title - {products.title}</h2>
            <p>Description - {products.description}</p>
            <p>Price - ${products.price}</p>
            <p>Ratings - {products.rating}</p>
            <p>Category - {products.category}</p>
            <p>Stock - {products.stock}</p>
            <h3>Images</h3>

            {products.images.map((image) => (
                <img key={image} src={image} width="150" />

            ))}
            <h3>Reviews</h3>
            <ul>
                {products.reviews.map((review) => (
                    <li key={review.reviewerEmail}>
                        {review.reviewerName} ({review.rating}/5): {review.comment}
                    </li>
                ))}
            </ul>   
        </>
    );

}

export default ProductDetailPage;