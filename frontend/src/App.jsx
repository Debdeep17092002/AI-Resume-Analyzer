import { NavLink, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import Jobs from "./pages/Jobs";
import Result from "./pages/Result";

export default function App() {
  return (
    <>
      <nav className="navbar">
        <span className="brand">AI Resume Analyzer</span>
        <NavLink to="/">Analyze</NavLink>
        <NavLink to="/jobs">Jobs</NavLink>
      </nav>
      <main className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/result" element={<Result />} />
          <Route path="/jobs" element={<Jobs />} />
        </Routes>
      </main>
    </>
  );
}