import React from "react";
import "@/components/header/style.css";

import email from "@/pages/home/assets/email.png";
import phone from "@/pages/home/assets/phone.png";
import Crowe from "@/assets/Crowe_Logo_blue.png";

const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="header-container">
        
        {/* Logo */}
        <div className="header-logo">
          <img src={Crowe} alt="Crowe Logo" />
        </div>

        {/* Contacts */}
        <div className="header-right">

          <div className="header-contacts-wrapper">
            
            <div className="header-contact">
              <img src={email} alt="email" />
              <span>Support@example.com</span>
            </div>

            <div className="header-contact">
              <img src={phone} alt="phone" />
              <span>+373 60 123 458</span>
            </div>

          </div>

          <button className="header-cta"
            onClick={() => window.open("https://t.me/BizScope_bot")}>
            Începe testul
          </button>

        </div>

      </div>
    </header>
  );
};

export default Header;
