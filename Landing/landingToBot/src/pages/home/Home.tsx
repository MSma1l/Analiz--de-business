import React from "react";

import crowe from "@/pages/home/assets/crowe.mp4"
import Header from "@/components/header/header";
import "@/pages/home/homeStyle.css"

const Home: React.FC = () => {
    return(
        <div className='home-page-to-landing'>
            < Header />
            <div className="main-section-hero">
                <video
                    className="background-video"
                    autoPlay
                    loop
                    muted
                    playsInline
                >
                    <source src={crowe} type="video/mp4" />
                </video>
                    <div className="main-section-hero">
                        <div className="content-section-hero">
                            <h1>Despre BizCheck_Bot</h1>
                            <p>
                            Acest bot a fost creat pentru a oferi o perspectivă rapidă și inteligentă asupra afacerii tale. Pe baza răspunsurilor introduse, sistemul analizează datele și stabilește nivelul de dezvoltare al businessului. În plus, utilizatorul poate vizualiza rezultatele sub formă de rapoarte clare și comparații relevante, obținând astfel o înțelegere mai bună a situației.
                            </p>
                            <button className="hero-btn">Aplică</button>
                        </div>
                    </div>
            </div>
                    <div className="about-landing-company">
                    <h1>About Us</h1>
                    <h3>
                        CROWE TURCAN MIKHAILENKO — din anul 2023 face parte din grupul internațional Crowe Global. Fondată în 1915, Crowe se numără astăzi printre primele 10 cele mai mari rețele globale de servicii profesionale.Oferim soluții avansate în domeniul fiscalității și consultanței juridice, ajutând antreprenorii să atingă noi culmi ale succesului.
                    </h3>
            </div>
<div className="services-landing-bot">
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
      <button>Aplică</button>
    </div>

    <div className="service-card">
      <span className="service-icon">📊</span>
      <h2>Evaluarea stării</h2>
      <p>
        Pe baza răspunsurilor oferite, sistemul evaluează starea afacerii
        și o încadrează într-un anumit nivel.
      </p>
      <button>Aplică</button>
    </div>

    <div className="service-card">
      <span className="service-icon">📋</span>
      <h2>Rapoarte</h2>
      <p>
        Generăm rapoarte structurate care sintetizează datele analizate
        și rezultatele obținute.
      </p>
      <button>Aplică</button>
    </div>
  </div>
</div>


        </div>
    )
}
export default Home;