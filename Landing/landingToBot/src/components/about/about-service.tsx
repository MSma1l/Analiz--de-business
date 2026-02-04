import React from "react";

import "@/components/about/styleAbout.css"

const AboutSecvice: React.FC = () => {

    return (

        <div className="overlay-hero">
            <div className="about-landing-company" id="about">
                    <h1>Despre Noi</h1>
                    <h3>
                        CROWE TURCAN MIKHAILENKO — din anul 2023 face parte din grupul internațional Crowe Global. Fondată în 1915, Crowe se numără astăzi printre primele 10 cele mai mari rețele globale de servicii profesionale.Oferim soluții avansate în domeniul fiscalității și consultanței juridice, ajutând antreprenorii să atingă noi culmi ale succesului.
                    </h3>
            </div>
            <div className="services-landing-bot" id = "service">
              <h1 className="services-title">Servicii oferite</h1>
              <h3 className="services-subtitle">Afacerea ta, explicată în cifre</h3>

              <div className="services-cards">
                <div className="service-card">
                  <span className="service-icon">📈</span>
                  <h2>Analiza afacerii</h2>
                  <p>
                    Analizăm datele introduse de utilizator pentru a identifica
                    punctele forte și punctele slabe ale afacerii.
                  </p>
                  <button
                  onClick={() => window.open('https://t.me/BizScope_bot')}
                  >Aplică</button>
                </div>

                <div className="service-card">
                  <span className="service-icon">📊</span>
                  <h2>Evaluarea stării</h2>
                  <p>
                    Pe baza răspunsurilor oferite, sistemul evaluează starea afacerii
                    și o încadrează într-un anumit nivel.
                  </p>
                  <button
                  onClick={() => window.open('https://t.me/BizScope_bot')}
                  >Aplică</button>
                </div>

                <div className="service-card">
                  <span className="service-icon">📋</span>
                  <h2>Rapoarte</h2>
                  <p>
                    Generăm rapoarte structurate care sintetizează datele analizate
                    și rezultatele obținute.
                  </p>
                  <button
                  onClick={() => window.open('https://t.me/BizScope_bot')}
                  >Aplică</button>
                </div>
              </div>
            </div>
          </div>
    )
}
export default AboutSecvice;