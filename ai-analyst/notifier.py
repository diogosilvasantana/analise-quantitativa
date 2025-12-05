import logging
import json
import redis
from config import Config

logger = logging.getLogger("AIAnalyst.Notifier")

class Notifier:
    def __init__(self):
        self.email_sender = Config.EMAIL_SENDER
        self.email_recipients = Config.EMAIL_RECIPIENTS
        
        # Connect to Redis
        try:
            self.redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=0,
                decode_responses=True
            )
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self.redis_client = None

    def format_html_report(self, analysis: dict) -> str:
        """
        Formats the JSON analysis into a beautiful HTML email.
        """
        sentiment_color = {
            "BULLISH": "green",
            "BEARISH": "red",
            "NEUTRAL": "gray",
            "VOLATILE": "orange"
        }.get(analysis.get("sentiment", "NEUTRAL"), "gray")

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                <h2 style="text-align: center; color: #0056b3;">🤖 AI Analyst - Relatório Pré-Abertura</h2>
                
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; text-align: center; margin-bottom: 20px;">
                    <h3 style="margin: 0;">Sentimento: <span style="color: {sentiment_color};">{analysis.get('sentiment')}</span></h3>
                    <p style="margin: 5px 0 0 0; font-size: 14px; color: #666;">Confiança: {analysis.get('confidence')}%</p>
                </div>

                <p><strong>Resumo:</strong> {analysis.get('summary')}</p>

                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">

                <div style="display: flex; justify-content: space-between;">
                    <div style="width: 48%;">
                        <h4 style="color: #0056b3;">WIN (Índice)</h4>
                        <ul style="list-style: none; padding: 0;">
                            <li><strong>Viés:</strong> {analysis.get('win_strategy', {}).get('bias')}</li>
                            <li><strong>Gap:</strong> {analysis.get('win_strategy', {}).get('gap_prediction')}</li>
                            <li><strong>Sup:</strong> {analysis.get('win_strategy', {}).get('support')}</li>
                            <li><strong>Res:</strong> {analysis.get('win_strategy', {}).get('resistance')}</li>
                        </ul>
                    </div>
                    <div style="width: 48%;">
                        <h4 style="color: #28a745;">WDO (Dólar)</h4>
                        <ul style="list-style: none; padding: 0;">
                            <li><strong>Viés:</strong> {analysis.get('wdo_strategy', {}).get('bias')}</li>
                            <li><strong>Gap:</strong> {analysis.get('wdo_strategy', {}).get('gap_prediction')}</li>
                            <li><strong>Sup:</strong> {analysis.get('wdo_strategy', {}).get('support')}</li>
                            <li><strong>Res:</strong> {analysis.get('wdo_strategy', {}).get('resistance')}</li>
                        </ul>
                    </div>
                </div>

                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">

                <div style="background-color: #e9ecef; padding: 15px; border-radius: 5px;">
                    <h4 style="margin-top: 0;">💡 Recomendação da IA</h4>
                    <p style="margin-bottom: 0;">{analysis.get('recommendation')}</p>
                </div>
                
                <p style="font-size: 12px; color: #999; text-align: center; margin-top: 30px;">
                    Gerado automaticamente por AI Trader Pro (Claude 3.5 Sonnet)
                </p>
            </div>
        </body>
        </html>
        """
        return html

    def send_report(self, analysis: dict):
        """
        Orchestrates the sending of the report.
        """
        logger.info("Preparing to send report...")
        
        # 1. Format HTML
        html_content = self.format_html_report(analysis)
        
        # 2. Save to Redis (for Frontend)
        if self.redis_client:
            try:
                # Inject timestamp
                from datetime import datetime
                analysis["timestamp"] = datetime.now().strftime("%H:%M")
                
                self.redis_client.set("ai_analyst_report", json.dumps(analysis))
                logger.info("💾 Relatório salvo no Redis (key: ai_analyst_report)")
            except Exception as e:
                logger.error(f"❌ Erro ao salvar no Redis: {e}")

        # 3. Save to Local File (for easy viewing)
        try:
            with open("latest_report.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info("💾 Relatório salvo em 'latest_report.html'")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar arquivo local: {e}")

        # 4. Send Email (Stub)
        # In a real scenario, use smtplib or an email service (SendGrid, AWS SES)
        logger.info(f"📧 Email content generated for {len(self.email_recipients)} recipients.")
        # print(html_content) # Debug
        
        # 5. Send Telegram (Stub)
        # requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", ...)
        logger.info("✈️ Telegram notification sent (Stub).")
        
        return True
