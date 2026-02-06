import React from "react";
import "@/components/CTABot/styleCTA.css";

const BotCTAAction: React.FC = () => {
  return (
    <section className="bot-cta-section" id="bot">
      <div className="bot-cta-container">
        {/* TEXT ZONE */}
        <div className="bot-cta-content">
          <h1 className="bot-cta-title">
            Evaluează-ți afacerea în <span>2 minute</span>
          </h1>

          <p className="bot-cta-subtitle">
            Răspunde la 20 de întrebări simple și primești automat un raport
            profesional despre starea afacerii tale, punctele forte și
            oportunitățile de creștere.
          </p>

          <button
            className="bot-cta-button"
            onClick={() => window.open("https://t.me/BizScope_bot")}
          >
            Începe evaluarea gratuită →
          </button>

          <div className="bot-cta-benefits">
            <div className="benefit">✔ 100% Gratuit</div>
            <div className="benefit">✔ Rezultat instant</div>
            <div className="benefit">✔ Fără înregistrare</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default BotCTAAction;
