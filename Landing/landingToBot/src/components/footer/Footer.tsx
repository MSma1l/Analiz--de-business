import "@/components/footer/styleFooter.css";
import { FaLinkedinIn, FaTelegramPlane, FaPhoneAlt, FaGlobe } from "react-icons/fa";
import { MdEmail } from "react-icons/md";
import QRcode from "@/pages/home/assets/QRcode.png";
import Crowe from "@/assets/Crowe_Standart_White.png";

const Footer = () => {
  const scrollToSection = (id:string) => {
    const element = document.getElementById(id);
    if (element) element.scrollIntoView({ behavior: "smooth", block: "center" });
  };

  return (
    <footer className="footer">
      <div className="footer-container">

        {/* Top Section */}
        <div className="footer-top">
          <div className="logo">
            <img src={Crowe} alt="Crowe Logo"/>
          </div>

          <div className="contact-info">
            <div className="contact-box">
              <div className="icon-circle email">
                <MdEmail />
              </div>
              <div>
                <p className="label">Email</p>
                <span>Support@Example.com</span>
              </div>
            </div>

            <div className="contact-box">
              <div className="icon-circle phone">
                <FaPhoneAlt />
              </div>
              <div>
                <p className="label">Telefon</p>
                <span>+373 6012345678</span>
              </div>
            </div>
          </div>
        </div>

        <hr />

        {/* Bottom Grid */}
        <div className="footer-grid">

          {/* Descriere + Social */}
          <div className="footer-col description">
            <p>
              Fiecare proiect pe care îl gestionăm reflectă angajamentul nostru
              pentru calitate, inovație și respectarea celor mai înalte standarde profesionale.
            </p>
            <div className="socials">
              <a href="https://www.linkedin.com/company/crowe-moldova" target="_blank"><FaLinkedinIn /></a>
              <a href="https://t.me/CROWE_TM" target="_blank"><FaTelegramPlane /></a>
              <a href="https://www.crowe.com/ua/crowemikhailenko/en-gb/moldova" target="_blank"><FaGlobe/></a>
            </div>
          </div>

          {/* Parteneri */}
          <div className="footer-col">
            <h4>Parteneri</h4>
            <ul>
              <li><a href="https://www.crowe.com/global" target="_blank">Crowe Global</a></li>
              <li><a href="https://www.crowe.com/ua/crowemikhailenko/en-gb/moldova" target="_blank">Crowe Turcan Mikhailenko</a></li>
            </ul>
          </div>

          {/* Link rapid */}
          <div className="footer-col">
            <h4>Link rapid</h4>
            <ul>
              <li><a onClick={() => scrollToSection("service")}>Servicii</a></li>
              <li><a onClick={() => scrollToSection("bot")}>BIZCHECK_Bot</a></li>
              <li><a onClick={() => scrollToSection("about")}>Despre Noi</a></li>
            </ul>
          </div>

          {/* QR */}
          <div className="footer-col qr-col">
            <p className="qr-text">Scanează pentru mai multe informații</p>
            <img src={QRcode} alt="QR Code"/>
          </div>
        </div>

        <hr />
        <p className="copyright">
          © {new Date().getFullYear()} Crowe Moldova. Toate drepturile rezervate.
        </p>
      </div>
    </footer>
  );
};

export default Footer;
