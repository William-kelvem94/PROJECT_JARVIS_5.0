#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Human Authorization Manager
========================================
Real functional system for managing human authorization of high-risk actions.

Responsibilities:
- Queue actions requiring human approval
- Track approval/rejection status
- Enforce protected file rules
- Analyze action complexity
- Provide authorization interfaces

Author: JARVIS 5.0 Evolution Layer
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from enum import Enum

from src.core.infrastructure.async_event_bus import event_bus, EventType, EventPriority

logger = logging.getLogger(__name__)


class ActionRiskLevel(Enum):
    """Risk levels for actions"""
    LOW = "low"              # < 3 files, < 10 lines
    MEDIUM = "medium"        # 3-5 files, 10-50 lines
    HIGH = "high"            # > 5 files, > 50 lines, or protected files
    CRITICAL = "critical"    # Core system files


class AuthorizationStatus(Enum):
    """Status of authorization requests"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    TIMEOUT = "timeout"


class AuthorizationRequest:
    """Represents a request for human authorization"""
    
    def __init__(self, action: Dict[str, Any], risk_level: ActionRiskLevel):
        self.id = hashlib.sha256(
            f"{action.get('arquivo')}{action.get('descricao')}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        self.action = action
        self.risk_level = risk_level
        self.status = AuthorizationStatus.PENDING
        self.created_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(hours=24)
        self.response_time = None
        self.reason = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "action": self.action,
            "risk_level": self.risk_level.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "response_time": self.response_time.isoformat() if self.response_time else None,
            "reason": self.reason
        }


class HumanAuthorizationManager:
    """
    Manages human authorization for high-risk actions.
    Real functional implementation for safety-critical operations.
    """
    
    def __init__(self, protected_files: Optional[List[str]] = None):
        self.pending_requests: Dict[str, AuthorizationRequest] = {}
        self.completed_requests: List[AuthorizationRequest] = []
        self.max_completed_history = 100
        
        # Protected file patterns (from system_manifest or defaults)
        self.protected_files = protected_files or [
            "src/core/infrastructure/*",
            "src/core/config/system_manifest.py",
            "src/evolution/*",
            "main.py",
            "src/core/engine/*"
        ]
        
        # Authorization callbacks
        self.approval_callbacks: List[Callable] = []
        self.rejection_callbacks: List[Callable] = []
        
        self.running = False
        self._cleanup_task = None
        
    async def start(self):
        """Start the authorization manager"""
        if self.running:
            return
            
        self.running = True
        
        # Subscribe to correction plans to intercept high-risk actions
        event_bus.subscribe(
            EventType.SYSTEM_DIAGNOSTIC_PLAN,
            self._handle_diagnostic_plan,
            priority_filter=[EventPriority.HIGH]
        )
        
        # Start cleanup task for expired requests
        self._cleanup_task = asyncio.create_task(self._cleanup_expired_requests())
        
        logger.info("🔐 Human Authorization Manager started")
        
    async def stop(self):
        """Stop the authorization manager"""
        self.running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
                
        logger.info("🔐 Human Authorization Manager stopped")
        
    async def _handle_diagnostic_plan(self, event):
        """Intercept diagnostic plans and check for high-risk actions"""
        if not self.running:
            return
            
        plan = event.data.get("plan", [])
        filtered_plan = []
        
        for action in plan:
            risk_level = self._assess_risk(action)
            
            if risk_level in [ActionRiskLevel.HIGH, ActionRiskLevel.CRITICAL]:
                # Requires human authorization
                request = AuthorizationRequest(action, risk_level)
                self.pending_requests[request.id] = request
                
                logger.warning(
                    f"🔐 Action requires authorization: {action.get('descricao')} "
                    f"[Risk: {risk_level.value}, ID: {request.id}]"
                )
                
                # Publish authorization request event
                event_bus.publish(
                    EventType.SYSTEM_WARNING,
                    data={
                        "type": "authorization_required",
                        "request": request.to_dict()
                    },
                    priority=EventPriority.HIGH,
                    source="authorization_manager"
                )
            else:
                # Low/medium risk - auto-approve
                filtered_plan.append(action)
                
        if filtered_plan:
            # Re-publish plan with only approved actions
            event_bus.publish(
                EventType.SYSTEM_DIAGNOSTIC_PLAN,
                data={"plan": filtered_plan},
                priority=EventPriority.HIGH,
                source="authorization_manager"
            )
            
    def _assess_risk(self, action: Dict[str, Any]) -> ActionRiskLevel:
        """Assess the risk level of an action"""
        file_path = action.get("arquivo", "")
        files_modified = action.get("files", [])
        code = action.get("codigo_corrigido", "")
        
        # Check if protected file
        if self._is_protected_file(file_path):
            return ActionRiskLevel.CRITICAL
            
        # Count files affected
        num_files = len(files_modified) if files_modified else (1 if file_path else 0)
        
        # Count lines changed
        num_lines = len(code.splitlines()) if code else 0
        
        # Assess based on complexity
        if num_files > 5 or num_lines > 50:
            return ActionRiskLevel.HIGH
        elif num_files >= 3 or num_lines >= 10:
            return ActionRiskLevel.MEDIUM
        else:
            return ActionRiskLevel.LOW
            
    def _is_protected_file(self, file_path: str) -> bool:
        """Check if a file is in the protected list"""
        from fnmatch import fnmatch
        
        for pattern in self.protected_files:
            if fnmatch(file_path, pattern):
                return True
        return False
        
    async def authorize(self, request_id: str, reason: Optional[str] = None) -> bool:
        """
        Approve an authorization request.
        
        Args:
            request_id: ID of the request to approve
            reason: Optional reason for approval
            
        Returns:
            True if approved, False if request not found or already processed
        """
        request = self.pending_requests.get(request_id)
        
        if not request:
            logger.warning(f"Authorization request {request_id} not found")
            return False
            
        if request.status != AuthorizationStatus.PENDING:
            logger.warning(f"Request {request_id} already processed: {request.status.value}")
            return False
            
        request.status = AuthorizationStatus.APPROVED
        request.response_time = datetime.now()
        request.reason = reason
        
        # Move to completed
        self.completed_requests.append(request)
        del self.pending_requests[request_id]
        
        # Trim history
        if len(self.completed_requests) > self.max_completed_history:
            self.completed_requests = self.completed_requests[-self.max_completed_history:]
            
        logger.info(f"✅ Action authorized: {request_id}")
        
        # Publish approved action back to execution pipeline
        event_bus.publish(
            EventType.SYSTEM_DIAGNOSTIC_PLAN,
            data={"plan": [request.action]},
            priority=EventPriority.HIGH,
            source="authorization_manager"
        )
        
        # Call approval callbacks
        for callback in self.approval_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(request)
                else:
                    callback(request)
            except Exception as e:
                logger.error(f"Error in approval callback: {e}")
                
        return True
        
    async def reject(self, request_id: str, reason: Optional[str] = None) -> bool:
        """
        Reject an authorization request.
        
        Args:
            request_id: ID of the request to reject
            reason: Optional reason for rejection
            
        Returns:
            True if rejected, False if request not found or already processed
        """
        request = self.pending_requests.get(request_id)
        
        if not request:
            logger.warning(f"Authorization request {request_id} not found")
            return False
            
        if request.status != AuthorizationStatus.PENDING:
            logger.warning(f"Request {request_id} already processed: {request.status.value}")
            return False
            
        request.status = AuthorizationStatus.REJECTED
        request.response_time = datetime.now()
        request.reason = reason
        
        # Move to completed
        self.completed_requests.append(request)
        del self.pending_requests[request_id]
        
        # Trim history
        if len(self.completed_requests) > self.max_completed_history:
            self.completed_requests = self.completed_requests[-self.max_completed_history:]
            
        logger.info(f"❌ Action rejected: {request_id}")
        
        # Call rejection callbacks
        for callback in self.rejection_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(request)
                else:
                    callback(request)
            except Exception as e:
                logger.error(f"Error in rejection callback: {e}")
                
        return True
        
    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get all pending authorization requests"""
        return [req.to_dict() for req in self.pending_requests.values()]
        
    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific request by ID"""
        request = self.pending_requests.get(request_id)
        if request:
            return request.to_dict()
            
        # Check completed requests
        for req in self.completed_requests:
            if req.id == request_id:
                return req.to_dict()
                
        return None
        
    async def _cleanup_expired_requests(self):
        """Periodically clean up expired requests"""
        while self.running:
            try:
                now = datetime.now()
                expired_ids = []
                
                for request_id, request in self.pending_requests.items():
                    if now > request.expires_at:
                        expired_ids.append(request_id)
                        request.status = AuthorizationStatus.EXPIRED
                        self.completed_requests.append(request)
                        
                for request_id in expired_ids:
                    del self.pending_requests[request_id]
                    logger.warning(f"⏰ Authorization request {request_id} expired")
                    
                # Trim history
                if len(self.completed_requests) > self.max_completed_history:
                    self.completed_requests = self.completed_requests[-self.max_completed_history:]
                    
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(60)
                
    def on_approval(self, callback: Callable):
        """Register a callback for approvals"""
        self.approval_callbacks.append(callback)
        
    def on_rejection(self, callback: Callable):
        """Register a callback for rejections"""
        self.rejection_callbacks.append(callback)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get authorization statistics"""
        total_requests = len(self.pending_requests) + len(self.completed_requests)
        
        approved = sum(1 for r in self.completed_requests if r.status == AuthorizationStatus.APPROVED)
        rejected = sum(1 for r in self.completed_requests if r.status == AuthorizationStatus.REJECTED)
        expired = sum(1 for r in self.completed_requests if r.status == AuthorizationStatus.EXPIRED)
        
        return {
            "total_requests": total_requests,
            "pending": len(self.pending_requests),
            "approved": approved,
            "rejected": rejected,
            "expired": expired,
            "approval_rate": (approved / len(self.completed_requests) * 100) if self.completed_requests else 0
        }


# Singleton instance
authorization_manager = HumanAuthorizationManager()
