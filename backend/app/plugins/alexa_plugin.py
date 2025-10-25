"""
Alexa Plugin - Integration with Amazon Alexa Skills Kit
"""
from typing import Dict, Any, Optional
import httpx
from datetime import datetime

from app.core.plugin_manager import PluginBase
from app.core.config import settings
from app.core.exceptions import PluginException


class AlexaPlugin(PluginBase):
    """
    Plugin for Amazon Alexa Skills Kit integration
    """
    
    name = "alexa"
    version = "1.0.0"
    description = "Amazon Alexa Skills Kit integration"
    author = "Jarvis Team"
    
    def __init__(self):
        super().__init__()
        self.client_id: Optional[str] = None
        self.client_secret: Optional[str] = None
        self.client: Optional[httpx.AsyncClient] = None
        self.access_token: Optional[str] = None
        self.token_expires: Optional[datetime] = None
    
    async def initialize(self) -> bool:
        """
        Initialize Alexa Skills Kit connection
        """
        try:
            self.client_id = settings.ALEXA_CLIENT_ID
            self.client_secret = settings.ALEXA_CLIENT_SECRET
            
            if not self.client_id or not self.client_secret:
                self.logger.warning("Alexa credentials not configured")
                self.enabled = False
                return False
            
            # Create async HTTP client
            self.client = httpx.AsyncClient(timeout=30.0)
            
            # Get access token
            await self._refresh_access_token()
            
            self.logger.info("Alexa plugin initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Alexa plugin: {str(e)}")
            self.enabled = False
            return False
    
    async def _refresh_access_token(self):
        """
        Refresh Alexa API access token
        """
        try:
            response = await self.client.post(
                "https://api.amazon.com/auth/o2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": "alexa::skills:readwrite"
                }
            )
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data["access_token"]
            
            # Token expires in seconds
            expires_in = data.get("expires_in", 3600)
            from datetime import timedelta
            self.token_expires = datetime.utcnow() + timedelta(seconds=expires_in - 300)  # Refresh 5 min early
            
            self.logger.info("Alexa access token refreshed")
            
        except Exception as e:
            raise PluginException(
                f"Failed to refresh Alexa access token: {str(e)}",
                plugin_name=self.name
            )
    
    async def _ensure_token(self):
        """
        Ensure access token is valid
        """
        if not self.access_token or not self.token_expires or datetime.utcnow() >= self.token_expires:
            await self._refresh_access_token()
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Alexa request
        
        Args:
            data: Request data with 'action' and parameters
                - action: 'handle_intent', 'send_notification', etc.
        
        Returns:
            Response data
        """
        if not self.enabled or not self.client:
            raise PluginException(
                "Alexa plugin not properly initialized",
                plugin_name=self.name
            )
        
        action = data.get("action")
        
        if action == "handle_intent":
            return await self._handle_intent(data)
        elif action == "send_notification":
            return await self._send_notification(data)
        elif action == "get_device_info":
            return await self._get_device_info(data)
        else:
            raise PluginException(
                f"Unknown action: {action}",
                plugin_name=self.name
            )
    
    async def _handle_intent(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Alexa intent
        
        Args:
            data: Intent data from Alexa request
        
        Returns:
            Response for Alexa
        """
        try:
            request_data = data.get("request", {})
            intent_name = request_data.get("intent", {}).get("name")
            slots = request_data.get("intent", {}).get("slots", {})
            
            # Process based on intent
            response_text = f"Received intent: {intent_name}"
            
            # Build Alexa response
            return {
                "version": "1.0",
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": response_text
                    },
                    "shouldEndSession": False
                }
            }
            
        except Exception as e:
            self.logger.error(f"Intent handling failed: {str(e)}")
            return {
                "version": "1.0",
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": "Sorry, I encountered an error processing your request."
                    },
                    "shouldEndSession": True
                }
            }
    
    async def _send_notification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send proactive notification to Alexa device
        
        Args:
            data: Notification data
        
        Returns:
            Send result
        """
        try:
            await self._ensure_token()
            
            user_id = data.get("user_id")
            message = data.get("message")
            
            if not user_id or not message:
                raise PluginException(
                    "Missing user_id or message",
                    plugin_name=self.name
                )
            
            # Send notification via Alexa API
            response = await self.client.post(
                f"https://api.amazonalexa.com/v1/proactiveEvents/stages/development",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "referenceId": f"jarvis-{datetime.utcnow().timestamp()}",
                    "event": {
                        "name": "AMAZON.MessageAlert.Activated",
                        "payload": {
                            "state": {
                                "status": "UNREAD",
                                "freshness": "NEW"
                            },
                            "messageGroup": {
                                "creator": {
                                    "name": "Jarvis AI"
                                },
                                "count": 1,
                                "urgency": "URGENT"
                            }
                        }
                    },
                    "relevantAudience": {
                        "type": "Unicast",
                        "payload": {
                            "user": user_id
                        }
                    }
                }
            )
            
            response.raise_for_status()
            
            return {
                "status": "success",
                "message": "Notification sent"
            }
            
        except httpx.HTTPError as e:
            self.logger.error(f"Notification sending failed: {str(e)}")
            raise PluginException(
                f"Failed to send notification: {str(e)}",
                plugin_name=self.name
            )
    
    async def _get_device_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get Alexa device information
        
        Args:
            data: Request data with device_id
        
        Returns:
            Device information
        """
        try:
            await self._ensure_token()
            
            device_id = data.get("device_id")
            
            if not device_id:
                raise PluginException(
                    "Missing device_id",
                    plugin_name=self.name
                )
            
            response = await self.client.get(
                f"https://api.amazonalexa.com/v1/devices/{device_id}",
                headers={
                    "Authorization": f"Bearer {self.access_token}"
                }
            )
            
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get device info: {str(e)}")
            raise PluginException(
                f"Failed to get device info: {str(e)}",
                plugin_name=self.name
            )
    
    def build_response(
        self,
        speech_text: str,
        card_title: Optional[str] = None,
        card_content: Optional[str] = None,
        should_end_session: bool = False
    ) -> Dict[str, Any]:
        """
        Build Alexa skill response
        
        Args:
            speech_text: Text for Alexa to speak
            card_title: Optional card title
            card_content: Optional card content
            should_end_session: Whether to end the session
        
        Returns:
            Alexa response JSON
        """
        response = {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": speech_text
                },
                "shouldEndSession": should_end_session
            }
        }
        
        if card_title and card_content:
            response["response"]["card"] = {
                "type": "Simple",
                "title": card_title,
                "content": card_content
            }
        
        return response
    
    async def shutdown(self):
        """
        Cleanup resources
        """
        if self.client:
            await self.client.aclose()
            self.client = None
        
        self.access_token = None
        self.token_expires = None
        
        self.logger.info("Alexa plugin shut down")

