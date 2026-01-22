"""
Email Integration - Integração com Gmail e Outlook para envio e leitura de emails
"""

import os
import base64
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.logger import logger

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import pickle
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    logger.warning("Google API não disponível. Instale: pip install google-auth-oauthlib google-api-python-client")


class EmailIntegration:
    """
    Integração com serviços de email.
    Suporta Gmail e Outlook.
    """
    
    def __init__(self, provider: str = "gmail", credentials_path: Optional[str] = None):
        """
        Inicializa integração com email.
        
        Args:
            provider: "gmail" ou "outlook"
            credentials_path: Caminho para arquivo de credenciais
        """
        self.provider = provider
        self.credentials_path = credentials_path or "./config/email_credentials.json"
        self.service = None
        
        # Inicializar provider
        if provider == "gmail":
            self._init_gmail()
        elif provider == "outlook":
            self._init_outlook()
        
        logger.info(f"EmailIntegration inicializado - Provider: {provider}")
    
    def _init_gmail(self):
        """Inicializa Gmail API."""
        if not GOOGLE_AVAILABLE:
            logger.error("Google API não disponível")
            return
        
        SCOPES = ['https://www.googleapis.com/auth/gmail.send', 
                  'https://www.googleapis.com/auth/gmail.readonly']
        creds = None
        
        # Token salvo
        token_path = './config/gmail_token.pickle'
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Se não há credenciais válidas, fazer login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    logger.error(f"Arquivo de credenciais não encontrado: {self.credentials_path}")
                    logger.info("Para usar Gmail, obtenha credenciais em: https://console.cloud.google.com/")
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Salvar credenciais
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Criar serviço
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail API inicializada")
    
    def _init_outlook(self):
        """Inicializa Outlook/Microsoft Graph API."""
        # TODO: Implementar integração com Microsoft Graph
        logger.warning("Outlook integration - não implementado ainda")
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        html: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Envia email.
        
        Args:
            to: Destinatário
            subject: Assunto
            body: Corpo do email
            cc: Lista de emails em cópia
            bcc: Lista de emails em cópia oculta
            html: Se True, corpo é HTML
        
        Returns:
            Dados do email enviado ou None em caso de erro
        """
        if not self.service:
            logger.error("Serviço de email não inicializado")
            return None
        
        try:
            # Criar mensagem
            message = MIMEMultipart()
            message['To'] = to
            message['Subject'] = subject
            
            if cc:
                message['Cc'] = ', '.join(cc)
            if bcc:
                message['Bcc'] = ', '.join(bcc)
            
            # Adicionar corpo
            mime_type = 'html' if html else 'plain'
            message.attach(MIMEText(body, mime_type, 'utf-8'))
            
            if self.provider == "gmail":
                # Enviar via Gmail API
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
                send_message = {'raw': raw_message}
                
                result = self.service.users().messages().send(
                    userId='me',
                    body=send_message
                ).execute()
                
                logger.info(f"Email enviado - ID: {result.get('id')}")
                return result
        
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return None
    
    def list_messages(
        self,
        max_results: int = 10,
        query: Optional[str] = None,
        label_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Lista mensagens da caixa de entrada.
        
        Args:
            max_results: Número máximo de mensagens
            query: Query de busca (ex: "is:unread", "from:exemplo@email.com")
            label_ids: IDs de labels para filtrar
        
        Returns:
            Lista de mensagens
        """
        if not self.service:
            logger.error("Serviço de email não inicializado")
            return []
        
        try:
            if self.provider == "gmail":
                result = self.service.users().messages().list(
                    userId='me',
                    maxResults=max_results,
                    q=query,
                    labelIds=label_ids or ['INBOX']
                ).execute()
                
                messages = result.get('messages', [])
                logger.info(f"{len(messages)} mensagens encontradas")
                return messages
        
        except Exception as e:
            logger.error(f"Erro ao listar mensagens: {e}")
            return []
    
    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera detalhes de uma mensagem.
        
        Args:
            message_id: ID da mensagem
        
        Returns:
            Dados da mensagem ou None
        """
        if not self.service:
            return None
        
        try:
            if self.provider == "gmail":
                message = self.service.users().messages().get(
                    userId='me',
                    id=message_id,
                    format='full'
                ).execute()
                
                return message
        
        except Exception as e:
            logger.error(f"Erro ao recuperar mensagem: {e}")
            return None
    
    def get_unread_count(self) -> int:
        """
        Retorna número de mensagens não lidas.
        
        Returns:
            Número de mensagens não lidas
        """
        messages = self.list_messages(query="is:unread")
        return len(messages)
    
    def mark_as_read(self, message_id: str) -> bool:
        """
        Marca mensagem como lida.
        
        Args:
            message_id: ID da mensagem
        
        Returns:
            True se marcada com sucesso
        """
        if not self.service:
            return False
        
        try:
            if self.provider == "gmail":
                self.service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
                
                logger.info(f"Mensagem marcada como lida: {message_id}")
                return True
        
        except Exception as e:
            logger.error(f"Erro ao marcar como lida: {e}")
            return False
    
    def delete_message(self, message_id: str) -> bool:
        """
        Deleta mensagem.
        
        Args:
            message_id: ID da mensagem
        
        Returns:
            True se deletada com sucesso
        """
        if not self.service:
            return False
        
        try:
            if self.provider == "gmail":
                self.service.users().messages().trash(
                    userId='me',
                    id=message_id
                ).execute()
                
                logger.info(f"Mensagem deletada: {message_id}")
                return True
        
        except Exception as e:
            logger.error(f"Erro ao deletar mensagem: {e}")
            return False
    
    def search_messages(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Busca mensagens.
        
        Args:
            query: Query de busca
            max_results: Número máximo de resultados
        
        Returns:
            Lista de mensagens encontradas
        """
        return self.list_messages(max_results=max_results, query=query)
    
    def get_latest_messages(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Retorna mensagens mais recentes.
        
        Args:
            count: Número de mensagens
        
        Returns:
            Lista de mensagens
        """
        messages = self.list_messages(max_results=count)
        
        # Buscar detalhes completos
        detailed_messages = []
        for msg in messages:
            details = self.get_message(msg['id'])
            if details:
                # Extrair informações principais
                headers = details.get('payload', {}).get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sem assunto')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Desconhecido')
                
                detailed_messages.append({
                    'id': msg['id'],
                    'subject': subject,
                    'from': from_email,
                    'snippet': details.get('snippet', '')
                })
        
        return detailed_messages
    
    def is_available(self) -> bool:
        """Verifica se integração está disponível."""
        return self.service is not None
