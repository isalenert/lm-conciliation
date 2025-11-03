import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import UploadPage from './pages/Upload';
import MappingPage from './pages/Mapping';
import ResultsPage from './pages/Results';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/mapping" element={<MappingPage />} />
        <Route path="/results" element={<ResultsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
