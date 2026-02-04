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
                <video
                    className="background-video"
                    autoPlay
                    loop
                    muted
                    playsInline
                  >
                    <source src={crowe} type="video/mp4" />
                </video>
            </div>
            <AboutSecvice />
            <BotCTAAction />
            <Footer />
        </div>
    )
}
export default Home;