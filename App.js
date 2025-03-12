import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import  Menu from './Pages/Menu';
import ModelComparison from './Pages/ModelComparison';
import DetailedComparison from './Pages/DetailedComparison';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Menu />} />
        <Route path="/model-comparison" element={<ModelComparison />} />
        <Route path="/detailed-comparison" element={<DetailedComparison />} />
      </Routes>
    </Router>
  );
}

export default App;
