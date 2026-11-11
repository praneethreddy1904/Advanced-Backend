import {Routes, Route, Link} from "react-router";
import ProductsPage from "./pages/ProductsPage.jsx";
import BrowserPage from "./pages/BrowserPage.jsx";
import ProductDetailPage from "./pages/ProductDetailPage.jsx";

function App() {

  return (
    <>
    <nav>
      <Link to="/">All Products</Link> | <Link to="/browser">Browser</Link>
    </nav>
    <Routes>
      <Route path="/" element={<ProductsPage/>} />
      <Route path="/browser" element={<BrowserPage/>} />
      <Route path="/products/:id" element={<ProductDetailPage/>} />
      <Route path="*" element={<h1>404 Not Found</h1>} />
    </Routes>
    </>
  )
}

export default App;
