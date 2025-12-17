import React, { useEffect, useState } from "react";
import {
  Camera,
  Smile,
  Brain,
  Gamepad2,
  PenTool,
  Settings,
  Play,
  ChevronDown,
  Sparkles,
  GraduationCap,
  Menu,
  X,
} from "lucide-react";
import "./App.css";

function App() {
  const [cameras, setCameras] = useState<MediaDeviceInfo[]>([]);
  const [selectedCameraIndex, setSelectedCameraIndex] = useState(0);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    navigator.mediaDevices.enumerateDevices().then((devices) => {
      const videoDevices = devices.filter((d) => d.kind === "videoinput");
      setCameras(videoDevices);
    });
  }, []);

  const handleCameraChange = (index: number) => {
    setSelectedCameraIndex(index);
    setIsDropdownOpen(false);
  };

  const features = [
    {
      icon: <Camera size={28} />,
      title: "Deteksi Emosi",
      description: "Analisis ekspresi wajah real-time dengan AI",
      onClick: () => window.api?.detectFace(selectedCameraIndex),
      color: "purple",
    },
    {
      icon: <Smile size={28} />,
      title: "Emoji Drawer",
      description: "Gambar emoji dengan gerakan tangan",
      onClick: () => window.api?.drawEmoji(),
      color: "orange",
    },
    {
      icon: <Brain size={28} />,
      title: "Quiz Game",
      description: "Uji pengetahuan dengan kuis interaktif",
      onClick: () => window.api?.runQuiz(),
      color: "blue",
    },
    {
      icon: <Gamepad2 size={28} />,
      title: "Guess Game",
      description: "Tebak gambar dan raih skor tertinggi",
      onClick: () => window.api?.runGuessGame(),
      color: "green",
    },
    {
      icon: <PenTool size={28} />,
      title: "Quiz Editor",
      description: "Buat dan kelola soal kuis custom",
      onClick: () => window.api?.runQuizEditor(),
      color: "pink",
    },
    {
      icon: <Settings size={28} />,
      title: "Guess Editor",
      description: "Kelola konten permainan tebak gambar",
      onClick: () => window.api?.runGuessEditor(),
      color: "cyan",
    },
  ];

  return (
    <div className="app">
      {/* Animated Background */}
      <div className="background">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
        <div className="blob blob-3"></div>
      </div>

      {/* Header */}
      <header className="header">
        <div className="header-container">
          <div className="logo">
            <GraduationCap size={32} />
            <span>Eureka English Education</span>
          </div>

          <button
            className="mobile-menu-btn"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>

          <nav className={`nav ${isMobileMenuOpen ? "nav-open" : ""}`}>

          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="main">
        {/* Hero Section */}
        <section className="hero">
          <div className="hero-content">
            <div className="hero-badge">
              <Sparkles size={16} />
              <span>E-Learning Tool</span>
            </div>
            <h1 className="hero-title">
              Belajar Lebih <span className="gradient-text">Interaktif</span>{" "}
              dengan Teknologi AI
            </h1>
            <p className="hero-description">
              Platform e-learning yang menggunakan Computer Vision dan AI untuk
              pengalaman belajar yang lebih personal dan menyenangkan.
            </p>
          </div>

          {/* Camera Selector Card */}
          <div className="camera-card">
            <div className="camera-card-header">
              <Camera size={20} />
              <span>Pengaturan Kamera</span>
            </div>
            <p className="camera-card-desc">
              Pilih kamera untuk fitur deteksi emosi
            </p>

            <div className="dropdown">
              <button
                className="dropdown-btn"
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              >
                <span>
                  {cameras[selectedCameraIndex]?.label ||
                    `Camera ${selectedCameraIndex}`}
                </span>
                <ChevronDown
                  size={20}
                  className={`dropdown-icon ${isDropdownOpen ? "rotate" : ""}`}
                />
              </button>

              {isDropdownOpen && cameras.length > 0 && (
                <div className="dropdown-menu">
                  {cameras.map((cam, index) => (
                    <button
                      key={index}
                      className={`dropdown-item ${index === selectedCameraIndex ? "selected" : ""}`}
                      onClick={() => handleCameraChange(index)}
                    >
                      <Camera size={16} />
                      <span>{cam.label || `Camera ${index}`}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="features">
          <div className="features-header">
            <h2 className="features-title">Fitur Pembelajaran</h2>
            <p className="features-subtitle">
              Pilih fitur yang ingin kamu gunakan
            </p>
          </div>

          <div className="features-grid">
            {features.map((feature, index) => (
              <div
                key={index}
                className={`feature-card feature-${feature.color}`}
                onClick={feature.onClick}
              >
                <div className="feature-icon">{feature.icon}</div>
                <div className="feature-content">
                  <h3 className="feature-title">{feature.title}</h3>
                  <p className="feature-description">{feature.description}</p>
                </div>
                <button className="feature-btn">
                  <Play size={18} />
                  <span>Mulai</span>
                </button>
              </div>
            ))}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>© Kelompok 3. Eureka English Education</p>
      </footer>
    </div>
  );
}

export default App;
