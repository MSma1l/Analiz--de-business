import React from "react";
import "@/components/footer/styleFooter.css";
import { FaLinkedinIn,FaTelegramPlane, FaPhoneAlt, FaGlobe } from "react-icons/fa";
import { MdEmail } from "react-icons/md";
import QRcode from "@/pages/home/assets/QRcode.png";
import Crowe_White from "@/assets/Crowe_White.png";
import Crowe_Logo_blue from "@/assets/Crowe_Logo_blue.png";
import Crowe_Black from "@/assets/Crowe_Black.png";
import Crowe_Standart_White from "@/assets/Crowe_Standart_White.png";

const Footer = () => {

    const scrollToSection = (id:string) => {
        const element = document.getElementById(id);
            if (element) {
                element.scrollIntoView({ 
                    behavior: "smooth",
                    block: "center"
            });
        }
    };

  return (
    <footer className="footer">
      <div className="footer-container">

        {/* Top Bar */}
        <div className="footer-top">
          <div className="logo">
            <img src={Crowe_Logo_blue} alt="Crowe Logo"/>
          </div>

          <div className="contact-info">
            <div className="contact-box">
              <div className="icon-circle">
                <MdEmail />
              </div>
              <div>
                <p className="label">Adresa electronică</p>
                <span>Support@Example.com</span>
              </div>
            </div>

            <div className="contact-box">
              <div className="icon-circle">
                <FaPhoneAlt />
              </div>
              <div>
                <p className="label">Numar mobil</p>
                <span>+3736012345678</span>
              </div>
            </div>
          </div>
        </div>

        <hr />

        {/* Bottom Grid */}
        <div className="footer-grid">

          {/* Descriere */}
          <div className="footer-col">
            <p>
              Fiecare proiect pe care îl gestionăm reflectă angajamentul nostru
              pentru calitate, inovație și respectarea celor mai înalte standarde
              profesionale.
            </p>

            <div className="socials">
              <a href="https://www.linkedin.com/company/crowe-moldova/?originalSubdomain=md"><FaLinkedinIn /></a>
              <a href="https://t.me/CROWE_TM"><FaTelegramPlane /></a>
              <a href="https://www.crowe.com/ua/crowemikhailenko/en-gb/moldova"><FaGlobe/></a>
            </div>
          </div>

          {/* Parteneri */}
          <div className="footer-col">
            <h4>Parteneri</h4>
            <ul>
              <li><a href="https://www.crowe.com/global">Crowe Global</a></li>
              <li><a href="https://www.crowe.com/ua/crowemikhailenko/en-gb/moldova">Crowe Turcan Mikhailenko</a></li>
            </ul>
          </div>

          {/* Link Rapid */}
          <div className="footer-col">
            <h4>Link rapid</h4>
            <ul>
              <li><a onClick={() => scrollToSection("service")}>
                Servicii</a></li>
              <li><a onClick={() => scrollToSection("bot")}>
                BIZCHECK_Bot
                </a>
                </li>
              <li><a onClick={() => scrollToSection("about")}>
                Despre Noi
                </a>
                </li>
            </ul>
          </div>

          {/* QR */}
          <div className="footer-col qr-col">
            <img
              src={QRcode}
              alt="QR Code"
            />
          </div>
        </div>

        <hr />

      </div>
    </footer>
  );
};

export default Footer;
