"""
Calendar Integration - Integração com Google Calendar e Outlook
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
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


class CalendarIntegration:
    """
    Integração com serviços de calendário.
    Suporta Google Calendar e Outlook (via Microsoft Graph API).
    """
    
    def __init__(self, provider: str = "google", credentials_path: Optional[str] = None):
        """
        Inicializa integração com calendário.
        
        Args:
            provider: "google" ou "outlook"
            credentials_path: Caminho para arquivo de credenciais
        """
        self.provider = provider
        self.credentials_path = credentials_path or "./config/calendar_credentials.json"
        self.service = None
        
        # Inicializar provider
        if provider == "google":
            self._init_google()
        elif provider == "outlook":
            self._init_outlook()
        
        logger.info(f"CalendarIntegration inicializado - Provider: {provider}")
    
    def _init_google(self):
        """Inicializa Google Calendar API."""
        if not GOOGLE_AVAILABLE:
            logger.error("Google API não disponível")
            return
        
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        
        # Token salvo
        token_path = './config/token.pickle'
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
                    logger.info("Para usar Google Calendar, obtenha credenciais em: https://console.cloud.google.com/")
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Salvar credenciais
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Criar serviço
        self.service = build('calendar', 'v3', credentials=creds)
        logger.info("Google Calendar API inicializada")
    
    def _init_outlook(self):
        """Inicializa Outlook/Microsoft Graph API."""
        # TODO: Implementar integração com Microsoft Graph
        logger.warning("Outlook integration - não implementado ainda")
    
    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Cria evento no calendário.
        
        Args:
            summary: Título do evento
            start_time: Data/hora de início
            end_time: Data/hora de término (padrão: 1 hora após início)
            description: Descrição do evento
            location: Local do evento
            attendees: Lista de emails dos participantes
        
        Returns:
            Dados do evento criado ou None em caso de erro
        """
        if not self.service:
            logger.error("Serviço de calendário não inicializado")
            return None
        
        # End time padrão
        if not end_time:
            end_time = start_time + timedelta(hours=1)
        
        # Montar evento
        event = {
            'summary': summary,
            'description': description or '',
            'location': location or '',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
        }
        
        # Adicionar participantes
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        try:
            if self.provider == "google":
                created_event = self.service.events().insert(
                    calendarId='primary',
                    body=event,
                    sendUpdates='all'  # Enviar convites
                ).execute()
                
                logger.info(f"Evento criado: {created_event.get('htmlLink')}")
                return created_event
        
        except Exception as e:
            logger.error(f"Erro ao criar evento: {e}")
            return None
    
    def list_events(
        self,
        max_results: int = 10,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Lista eventos do calendário.
        
        Args:
            max_results: Número máximo de eventos
            time_min: Data/hora mínima (padrão: agora)
            time_max: Data/hora máxima (padrão: sem limite)
        
        Returns:
            Lista de eventos
        """
        if not self.service:
            logger.error("Serviço de calendário não inicializado")
            return []
        
        if not time_min:
            time_min = datetime.utcnow()
        
        try:
            if self.provider == "google":
                events_result = self.service.events().list(
                    calendarId='primary',
                    timeMin=time_min.isoformat() + 'Z',
                    timeMax=time_max.isoformat() + 'Z' if time_max else None,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                events = events_result.get('items', [])
                logger.info(f"{len(events)} eventos encontrados")
                return events
        
        except Exception as e:
            logger.error(f"Erro ao listar eventos: {e}")
            return []
    
    def get_next_event(self) -> Optional[Dict[str, Any]]:
        """
        Retorna próximo evento agendado.
        
        Returns:
            Dados do próximo evento ou None
        """
        events = self.list_events(max_results=1)
        return events[0] if events else None
    
    def delete_event(self, event_id: str) -> bool:
        """
        Deleta evento do calendário.
        
        Args:
            event_id: ID do evento
        
        Returns:
            True se deletado com sucesso
        """
        if not self.service:
            return False
        
        try:
            if self.provider == "google":
                self.service.events().delete(
                    calendarId='primary',
                    eventId=event_id,
                    sendUpdates='all'
                ).execute()
                
                logger.info(f"Evento deletado: {event_id}")
                return True
        
        except Exception as e:
            logger.error(f"Erro ao deletar evento: {e}")
            return False
    
    def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        description: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Atualiza evento existente.
        
        Args:
            event_id: ID do evento
            summary: Novo título
            start_time: Nova data/hora de início
            end_time: Nova data/hora de término
            description: Nova descrição
        
        Returns:
            Evento atualizado ou None em caso de erro
        """
        if not self.service:
            return None
        
        try:
            if self.provider == "google":
                # Buscar evento atual
                event = self.service.events().get(
                    calendarId='primary',
                    eventId=event_id
                ).execute()
                
                # Atualizar campos
                if summary:
                    event['summary'] = summary
                if description:
                    event['description'] = description
                if start_time:
                    event['start']['dateTime'] = start_time.isoformat()
                if end_time:
                    event['end']['dateTime'] = end_time.isoformat()
                
                # Salvar mudanças
                updated_event = self.service.events().update(
                    calendarId='primary',
                    eventId=event_id,
                    body=event,
                    sendUpdates='all'
                ).execute()
                
                logger.info(f"Evento atualizado: {event_id}")
                return updated_event
        
        except Exception as e:
            logger.error(f"Erro ao atualizar evento: {e}")
            return None
    
    def is_available(self) -> bool:
        """Verifica se integração está disponível."""
        return self.service is not None
