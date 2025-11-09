"""
Serviço de envio de emails usando SendGrid
Autor: LM Conciliation
Data: 2025-01-08
"""

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import os
from typing import Optional


class EmailService:
    """
    Classe responsável por todo envio de emails da aplicação
    Usa SendGrid como provedor de email
    """
    
    def __init__(self):
        """
        Inicializa o serviço de email
        Busca configurações das variáveis de ambiente
        """
        # API Key do SendGrid (obrigatória)
        self.api_key = os.getenv("SENDGRID_API_KEY")
        if not self.api_key:
            raise ValueError("❌ SENDGRID_API_KEY não configurada no .env")
        
        # Email remetente (ex: noreply@lmconciliation.com)
        self.sender_email = os.getenv("SENDER_EMAIL", "noreply@lmconciliation.com")
        
        # Nome do remetente (ex: LM Conciliation)
        self.sender_name = os.getenv("SENDER_NAME", "LM Conciliation")
        
        # URL do frontend (para montar links)
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        
        print(f"✅ EmailService inicializado")
        print(f"   Remetente: {self.sender_name} <{self.sender_email}>")
        print(f"   Frontend: {self.frontend_url}")
    
    def send_reset_password_email(self, to_email: str, reset_token: str) -> bool:
        """
        Envia email de reset de senha
        
        Args:
            to_email: Email do destinatário
            reset_token: Token JWT para reset
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            # Montar link completo com token
            reset_link = f"{self.frontend_url}/reset-password?token={reset_token}"
            
            # HTML do email (design profissional)
            html_content = f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        margin: 0;
                        padding: 0;
                        background-color: #f4f4f4;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 20px auto;
                        background: white;
                        border-radius: 8px;
                        overflow: hidden;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
                        color: white;
                        padding: 30px 20px;
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                        font-weight: 600;
                    }}
                    .content {{
                        padding: 40px 30px;
                    }}
                    .content h2 {{
                        color: #16a34a;
                        font-size: 24px;
                        margin-top: 0;
                        margin-bottom: 20px;
                    }}
                    .content p {{
                        margin-bottom: 15px;
                        color: #555;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 14px 40px;
                        background: #16a34a;
                        color: white !important;
                        text-decoration: none;
                        border-radius: 6px;
                        margin: 25px 0;
                        font-weight: 600;
                        font-size: 16px;
                        transition: background 0.3s;
                    }}
                    .button:hover {{
                        background: #15803d;
                    }}
                    .link-box {{
                        background: #f9fafb;
                        padding: 15px;
                        border-radius: 6px;
                        word-break: break-all;
                        font-size: 13px;
                        color: #666;
                        border-left: 4px solid #16a34a;
                        margin: 20px 0;
                    }}
                    .warning {{
                        background: #fef3c7;
                        border-left: 4px solid #f59e0b;
                        padding: 15px;
                        margin: 20px 0;
                        border-radius: 4px;
                    }}
                    .warning strong {{
                        color: #b45309;
                    }}
                    .footer {{
                        background: #f9fafb;
                        padding: 25px;
                        text-align: center;
                        font-size: 13px;
                        color: #666;
                        border-top: 1px solid #e5e7eb;
                    }}
                    .footer p {{
                        margin: 5px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 LM Conciliation</h1>
                    </div>
                    
                    <div class="content">
                        <h2>Redefinir Senha</h2>
                        
                        <p>Olá!</p>
                        
                        <p>Você solicitou a redefinição de senha da sua conta no <strong>LM Conciliation</strong>.</p>
                        
                        <p>Para criar uma nova senha, clique no botão abaixo:</p>
                        
                        <div style="text-align: center;">
                            <a href="{reset_link}" class="button">Redefinir Minha Senha</a>
                        </div>
                        
                        <p>Ou copie e cole este link no seu navegador:</p>
                        
                        <div class="link-box">
                            {reset_link}
                        </div>
                        
                        <div class="warning">
                            <strong>⚠️ Atenção:</strong> Este link expira em <strong>1 hora</strong> por segurança.
                        </div>
                        
                        <p>Se você <strong>não solicitou</strong> esta redefinição, ignore este email. Sua senha permanecerá a mesma.</p>
                        
                        <p style="margin-top: 30px;">
                            Atenciosamente,<br>
                            <strong>Equipe LM Conciliation</strong>
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p><strong>LM Conciliation</strong></p>
                        <p>Sistema de Conciliação Bancária Automatizada</p>
                        <p style="margin-top: 15px; color: #999;">
                            Este é um email automático. Por favor, não responda.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Criar mensagem
            message = Mail(
                from_email=Email(self.sender_email, self.sender_name),
                to_emails=To(to_email),
                subject="🔐 Redefinição de Senha - LM Conciliation",
                html_content=Content("text/html", html_content)
            )
            
            # Enviar via SendGrid
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            
            # Verificar se enviou
            if response.status_code == 202:
                print(f"✅ Email de reset enviado para {to_email}")
                return True
            else:
                print(f"⚠️ Resposta inesperada: {response.status_code}")
                return False
            
        except Exception as e:
            print(f"❌ Erro ao enviar email: {str(e)}")
            return False
    
    def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """
        Envia email de boas-vindas após cadastro
        
        Args:
            to_email: Email do novo usuário
            user_name: Nome do usuário
            
        Returns:
            True se enviado com sucesso
        """
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        margin: 0;
                        padding: 0;
                        background-color: #f4f4f4;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 20px auto;
                        background: white;
                        border-radius: 8px;
                        overflow: hidden;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
                        color: white;
                        padding: 30px 20px;
                        text-align: center;
                    }}
                    .content {{
                        padding: 40px 30px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 14px 40px;
                        background: #16a34a;
                        color: white !important;
                        text-decoration: none;
                        border-radius: 6px;
                        margin: 25px 0;
                        font-weight: 600;
                    }}
                    .footer {{
                        background: #f9fafb;
                        padding: 25px;
                        text-align: center;
                        font-size: 13px;
                        color: #666;
                        border-top: 1px solid #e5e7eb;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Bem-vindo(a)!</h1>
                    </div>
                    
                    <div class="content">
                        <h2>Olá, {user_name}!</h2>
                        
                        <p>Sua conta foi criada com sucesso no <strong>LM Conciliation</strong>!</p>
                        
                        <p>Agora você pode fazer login e começar a automatizar suas conciliações bancárias.</p>
                        
                        <div style="text-align: center;">
                            <a href="{self.frontend_url}/login" class="button">Fazer Login</a>
                        </div>
                        
                        <p>Se precisar de ajuda, consulte nossa documentação ou entre em contato.</p>
                        
                        <p style="margin-top: 30px;">
                            Bons trabalhos!<br>
                            <strong>Equipe LM Conciliation</strong>
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p><strong>LM Conciliation</strong></p>
                        <p>Sistema de Conciliação Bancária Automatizada</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=Email(self.sender_email, self.sender_name),
                to_emails=To(to_email),
                subject="🎉 Bem-vindo ao LM Conciliation!",
                html_content=Content("text/html", html_content)
            )
            
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            
            if response.status_code == 202:
                print(f"✅ Email de boas-vindas enviado para {to_email}")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Erro ao enviar email de boas-vindas: {str(e)}")
            return False


# Criar instância global do serviço
# Isso permite usar email_service em qualquer lugar do código
email_service = EmailService()
