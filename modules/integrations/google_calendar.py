"""
Google Calendar Integration
Inspired by Gladiator07/JARVIS
Provides calendar event management and reminders
"""

import os
import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import json


class GoogleCalendarIntegration:
    """
    Google Calendar integration for event management.
    
    Features:
    - Get upcoming events
    - Create new events
    - Delete events
    - Event reminders
    """
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Google Calendar integration.
        
        Args:
            credentials_path: Path to Google API credentials JSON
        """
        self.credentials_path = credentials_path or os.getenv(
            'GOOGLE_CALENDAR_CREDENTIALS',
            'config/google_credentials.json'
        )
        self.service = None
        self.is_available = False
        
        # Try to initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize Google Calendar API."""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            
            # If modifying these scopes, delete the token file
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            
            creds = None
            token_path = 'config/google_token.json'
            
            # Load existing credentials
            if os.path.exists(token_path):
                try:
                    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
                except Exception as e:
                    print(f"[Calendar] Error loading token: {e}")
            
            # If no valid credentials, let user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        print(f"[Calendar] Error refreshing token: {e}")
                        creds = None
                
                if not creds and os.path.exists(self.credentials_path):
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_path, SCOPES
                        )
                        creds = flow.run_local_server(port=0)
                    except Exception as e:
                        print(f"[Calendar] Error in auth flow: {e}")
                        return
                
                # Save credentials for future use
                if creds:
                    try:
                        os.makedirs('config', exist_ok=True)
                        with open(token_path, 'w') as token:
                            token.write(creds.to_json())
                    except Exception as e:
                        print(f"[Calendar] Error saving token: {e}")
            
            if creds:
                self.service = build('calendar', 'v3', credentials=creds)
                self.is_available = True
                print("[Calendar] ✓ Google Calendar initialized successfully")
            else:
                print("[Calendar] ✗ Could not initialize Google Calendar")
                
        except ImportError:
            print("[Calendar] Google API libraries not installed")
            print("Install with: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        except Exception as e:
            print(f"[Calendar] Initialization error: {e}")
    
    def get_upcoming_events(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get upcoming calendar events.
        
        Args:
            max_results: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        if not self.is_available:
            return []
        
        try:
            # Get current time
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            
            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Format events
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                formatted_events.append({
                    'id': event.get('id'),
                    'summary': event.get('summary', 'No Title'),
                    'start': start,
                    'location': event.get('location', ''),
                    'description': event.get('description', '')
                })
            
            return formatted_events
            
        except Exception as e:
            print(f"[Calendar] Error getting events: {e}")
            return []
    
    def get_events_today(self) -> List[Dict[str, Any]]:
        """Get events for today."""
        if not self.is_available:
            return []
        
        try:
            # Start and end of today
            now = datetime.datetime.now()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Format for API
            time_min = start_of_day.isoformat() + 'Z'
            time_max = end_of_day.isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                formatted_events.append({
                    'id': event.get('id'),
                    'summary': event.get('summary', 'No Title'),
                    'start': start,
                    'location': event.get('location', ''),
                    'description': event.get('description', '')
                })
            
            return formatted_events
            
        except Exception as e:
            print(f"[Calendar] Error getting today's events: {e}")
            return []
    
    def create_event(
        self,
        summary: str,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        description: str = '',
        location: str = ''
    ) -> Optional[str]:
        """
        Create a new calendar event.
        
        Args:
            summary: Event title
            start_time: Event start time
            end_time: Event end time
            description: Event description
            location: Event location
            
        Returns:
            Event ID if successful, None otherwise
        """
        if not self.is_available:
            return None
        
        try:
            event = {
                'summary': summary,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            print(f"[Calendar] Event created: {created_event.get('htmlLink')}")
            return created_event.get('id')
            
        except Exception as e:
            print(f"[Calendar] Error creating event: {e}")
            return None
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete a calendar event.
        
        Args:
            event_id: ID of event to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            print(f"[Calendar] Event deleted: {event_id}")
            return True
            
        except Exception as e:
            print(f"[Calendar] Error deleting event: {e}")
            return False
    
    def format_events_for_speech(self, events: List[Dict[str, Any]]) -> str:
        """
        Format events for text-to-speech.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Formatted string for TTS
        """
        if not events:
            return "Você não tem eventos próximos."
        
        response = f"Você tem {len(events)} evento(s): "
        
        for i, event in enumerate(events, 1):
            summary = event.get('summary', 'Sem título')
            start = event.get('start', '')
            
            # Parse time
            try:
                if 'T' in start:
                    dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                    time_str = dt.strftime('%H:%M')
                    response += f"{i}. {summary} às {time_str}. "
                else:
                    response += f"{i}. {summary}. "
            except:
                response += f"{i}. {summary}. "
        
        return response
    
    def get_next_event(self) -> Optional[Dict[str, Any]]:
        """Get the next upcoming event."""
        events = self.get_upcoming_events(max_results=1)
        return events[0] if events else None


# Example usage
if __name__ == "__main__":
    # Initialize
    calendar = GoogleCalendarIntegration()
    
    if calendar.is_available:
        # Get upcoming events
        print("\n=== Upcoming Events ===")
        events = calendar.get_upcoming_events(5)
        for event in events:
            print(f"- {event['summary']} at {event['start']}")
        
        # Get today's events
        print("\n=== Today's Events ===")
        today_events = calendar.get_events_today()
        for event in today_events:
            print(f"- {event['summary']} at {event['start']}")
        
        # Format for speech
        print("\n=== Speech Format ===")
        print(calendar.format_events_for_speech(events))
    else:
        print("Google Calendar not available. Check credentials.")
