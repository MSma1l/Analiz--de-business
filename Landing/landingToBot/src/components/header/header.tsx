import  React from "react";

import "@/components/header/style.css"
import email from "@/pages/home/assets/email.png"
import phone from "@/pages/home/assets/phone.png"
import Crowe_White from "@/assets/Crowe_White.png"


const Header: React.FC = () => {

    return(
      <div className="header-landing-page">
        
        <div className="header-landing-logo">
          <img src={Crowe_White} alt="Crowe Logo" />

          {/* <div className="select-language">
            <select>
              <option value="ro">RO</option>
              <option value="ru">RU</option>
            </select>
          </div> */}
        </div>

        <div className="header-contacts">
          <div className="contact-item">
            <div className="contact-icon">
              <img src={email} alt="email" />
            </div>
            <div className="contact-text">
              <span>Adresa electronică</span>
              <strong>Support@Example.com</strong>
            </div>
          </div>

          <div className="contact-item">
            <div className="contact-icon">
              <img src={phone} alt="phone" />
            </div>
            <div className="contact-text">
              <span>Număr Mobil</span>
              <strong>+37360123458</strong>
            </div>
          </div>
        </div>
      </div>
    )
}
export default Header;