import React from "react";

import "@/components/CTABot/styleCTA.css"

const BotCTAAction: React.FC = () => {

    return (
        <section className="bot-cta-section" id="bot">
      <h1 className="bot-cta-title">
        Evaluează-ți afacerea în 2 minute
      </h1>

      <p className="bot-cta-subtitle">
        Răspunde la 20 de întrebări simple și primești automat un raport
        despre starea afacerii tale.
      </p>

      <button className="bot-cta-button"
        onClick={() =>
          window.open("https://t.me/BizScope_bot")
        }
      >
        👉 Începe testul 👈
      </button>

      <div className="bot-cta-benefits">
        <span>✔ Gratuit</span>
        <span>✔ Rapid</span>
        <span>✔ Fără înregistrare</span>
      </div>
    </section>
    );
};

export default BotCTAAction;