import React from "react";
import "@/components/about/styleAbout.css";

const AboutSecvice: React.FC = () => {
  return (
    <section className="about-services-section">

      {/* ===== ABOUT ===== */}
      <div className="about-container" id="about">

        <h2 className="section-title">Despre Crowe</h2>

        <p className="about-text">
          CROWE TURCAN MIKHAILENKO face parte din grupul internațional
          Crowe Global — una dintre primele 10 rețele globale de servicii
          profesionale, fondată în 1915.
        </p>

        {/* Trust badges */}
        <div className="about-trust">

          <div className="trust-item">
            <h3>Top 10</h3>
            <span>Rețea globală</span>
          </div>

          <div className="trust-item">
            <h3>150+</h3>
            <span>Țări</span>
          </div>

          <div className="trust-item">
            <h3>100+</h3>
            <span>Ani experiență</span>
          </div>

        </div>
      </div>

      {/* ===== SERVICES ===== */}
      <div className="services-container" id="service">

        <h2 className="section-title">Servicii oferite</h2>
        <p className="section-subtitle">
          Afacerea ta, explicată în cifre și indicatori clari
        </p>

        <div className="services-grid">

          {/* Card 1 */}
          <div className="service-card">
            <div className="service-icon">📈</div>
            <h3>Analiza afacerii</h3>
            <p>
              Identificăm punctele forte și riscurile pe baza datelor introduse.
            </p>
            <button onClick={() => window.open('https://t.me/BizScope_bot')}>
              Aplică
            </button>
          </div>

          {/* Card 2 */}
          <div className="service-card">
            <div className="service-icon">📊</div>
            <h3>Evaluarea stării</h3>
            <p>
              Determinăm nivelul de performanță al companiei tale.
            </p>
            <button onClick={() => window.open('https://t.me/BizScope_bot')}>
              Aplică
            </button>
          </div>

          {/* Card 3 */}
          <div className="service-card">
            <div className="service-icon">📋</div>
            <h3>Rapoarte</h3>
            <p>
              Primești rapoarte profesionale structurate și clare.
            </p>
            <button onClick={() => window.open('https://t.me/BizScope_bot')}>
              Aplică
            </button>
          </div>

        </div>
      </div>

    </section>
  );
};

export default AboutSecvice;
