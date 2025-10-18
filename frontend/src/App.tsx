import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import ChatWidget from './components/ChatWidget';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Jobs from './pages/Jobs';
import CreateJob from './pages/CreateJob';
import CreateResume from './pages/CreateResume';
import JobDetails from './pages/JobDetails';
import EmployerDashboard from './pages/EmployerDashboard';
import { JobSeekerProfile } from './pages/JobSeekerProfile';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/jobs/:id" element={<JobDetails />} />
            <Route path="/create-job" element={<CreateJob />} />
            <Route path="/create-resume" element={<CreateResume />} />
            <Route path="/employer/dashboard" element={<EmployerDashboard />} />
            <Route path="/employer-dashboard" element={<EmployerDashboard />} />
            <Route path="/dashboard" element={<JobSeekerProfile />} />
            <Route path="/profile" element={<JobSeekerProfile />} />
          </Routes>
          <ChatWidget />
        </Layout>
      </Router>
    </AuthProvider>
  );
}

export default App;
