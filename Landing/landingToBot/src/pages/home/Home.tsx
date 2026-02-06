import React from "react";

import crowe from "@/pages/home/assets/crowe.mp4"
import Header from "@/components/header/header";
import AboutSecvice from "@/components/about/about-service";
import BotCTAAction from "@/components/CTABot/BotCTAAction"
import Footer from "@/components/footer/Footer";
import "@/pages/home/homeStyle.css"

const Home: React.FC = () => {
    return(
        <div className='home-page-to-landing'>
            < Header />
                <div className="main-section-hero">

                {/* Background video */}
                <video
                    className="background-video"
                    autoPlay
                    loop
                    muted
                    playsInline
                >
                    <source src={crowe} type="video/mp4" />
                </video>

                {/* Overlay dark */}
                <div className="hero-overlay"></div>

                {/* Content */}
                <div className="hero-content">

                    <h1 className="hero-title">
                    Evaluează performanța afacerii tale
                    </h1>

                    <p className="hero-subtitle">
                    Completează testul și primești instant un raport profesional
                    realizat pe metodologia Crowe Turcan Mikhailenko
                    </p>

                    <div className="hero-actions">
                    <button className="hero-cta"
                    onClick={() => window.open("https://t.me/BizScope_bot")}
                    >
                        Începe testul gratuit
                    </button>
                    </div>

                    {/* Trust badges */}
                    <div className="hero-trust">
                    <span>✔ Gratuit</span>
                    <span>✔ Fără înregistrare</span>
                    <span>✔ Raport instant</span>
                    </div>

                </div>
                </div>

            <AboutSecvice />
            <BotCTAAction />
            <Footer />
        </div>
    )
}
export default Home;