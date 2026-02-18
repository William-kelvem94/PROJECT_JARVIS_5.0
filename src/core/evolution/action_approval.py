"""
ActionApprovalManager

- Mantém ações pendentes que aguardam aprovação humana (via EventBus)
- Escuta `EventType.ACTION_APPROVAL_RESPONSE` e executa callbacks quando aprovado
- Publica status (SYSTEM_CORRECTION_SUCCEEDED / FAILED)

API principal (singleton):
- action_approval_manager.register_pending(request_id, callback, meta)
- action_approval_manager.start_listening()
- action_approval_manager.approve_via_bus(request_id, approved=True)

Design: conservador — execuções são feitas em thread separada; falhas geram eventos de falha.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Callable, Dict, Optional

from src.core.infrastructure.async_event_bus import (
    get_event_bus,
    EventType,
    EventPriority,
)
from src.core.infrastructure.async_event_bus import Event

logger = logging.getLogger(__name__)


class ActionApprovalManager:
    def __init__(self):
        # request_id -> {callback, meta, created_at}
        self._pending: Dict[str, Dict[str, Any]] = {}
        self._listening = False

    def start_listening(self):
        """Subscribe to approval responses on the EventBus (idempotent)."""
        if self._listening:
            return

        bus = get_event_bus()
        # subscribe only if bus appears runnable; tests will call this after
        # bus.start()
        try:
            bus.subscribe([EventType.ACTION_APPROVAL_RESPONSE], self._on_response)
            self._listening = True
            logger.info("ActionApprovalManager: listening for approval responses")
        except Exception as e:
            logger.debug(f"ActionApprovalManager: could not subscribe to EventBus: {e}")

    def register_pending(
        self,
        request_id: str,
        callback: Callable[[], Any],
        meta: Optional[Dict] = None,
        ttl_seconds: int = 86400,
    ):
        """Register a pending action that will be executed when approval is received.

        Returns True if registered, False if a pending with same id exists.
        """
        if request_id in self._pending:
            return False
        self._pending[request_id] = {
            "callback": callback,
            "meta": meta or {},
            "created_at": time.time(),
            "ttl": ttl_seconds,
        }
        logger.debug(f"ActionApprovalManager: registered pending action {request_id}")
        return True

    def _on_response(self, event: Event):
        try:
            data = event.data or {}
            req_id = data.get("request_id")
            approved = bool(data.get("approved"))

            if not req_id:
                logger.debug(
                    "ActionApprovalManager: approval response missing request_id"
                )
                return

            if req_id not in self._pending:
                logger.debug(
                    f"ActionApprovalManager: no pending action for request_id={req_id}"
                )
                return

            entry = self._pending.pop(req_id)
            cb = entry.get("callback")

            if approved:
                # execute callback in background thread
                def _run_cb():
                    try:
                        if cb is not None:
                            result = cb()
                            logger.info(
                                f"ActionApprovalManager: action {req_id} executed (result={result})"
                            )
                            # publish success
                            try:
                                get_event_bus().publish(
                                    EventType.SYSTEM_CORRECTION_SUCCEEDED,
                                    {"request_id": req_id, "result": str(result)},
                                    priority=EventPriority.HIGH,
                                    source="action_approval",
                                )
                            except Exception:
                                pass
                        else:
                            logger.error(
                                f"ActionApprovalManager: callback for action {req_id} is None"
                            )
                            try:
                                get_event_bus().publish(
                                    EventType.SYSTEM_CORRECTION_FAILED,
                                    {"request_id": req_id, "error": "callback is None"},
                                    priority=EventPriority.CRITICAL,
                                    source="action_approval",
                                )
                            except Exception:
                                pass
                    except Exception as e:
                        logger.error(
                            f"ActionApprovalManager: action {req_id} failed: {e}"
                        )
                        try:
                            get_event_bus().publish(
                                EventType.SYSTEM_CORRECTION_FAILED,
                                {"request_id": req_id, "error": str(e)},
                                priority=EventPriority.CRITICAL,
                                source="action_approval",
                            )
                        except Exception:
                            pass

                t = threading.Thread(target=_run_cb, daemon=True)
                t.start()
            else:
                logger.info(
                    f"ActionApprovalManager: action {req_id} explicitly rejected"
                )
                try:
                    get_event_bus().publish(
                        EventType.SYSTEM_CORRECTION_FAILED,
                        {"request_id": req_id, "error": "rejected"},
                        priority=EventPriority.NORMAL,
                        source="action_approval",
                    )
                except Exception:
                    pass

        except Exception as e:
            logger.error(
                f"ActionApprovalManager: failed to handle approval response: {e}"
            )

    def approve_via_bus(
        self, request_id: str, approved: bool = True, approver: Optional[str] = None
    ):
        """Convenience: publish approval response on the EventBus."""
        try:
            get_event_bus().publish(
                EventType.ACTION_APPROVAL_RESPONSE,
                {"request_id": request_id, "approved": approved, "approver": approver},
                source="action_approval_manager",
            )
            return True
        except Exception as e:
            logger.debug(
                f"ActionApprovalManager: failed to publish approval response: {e}"
            )
            return False

    def approve_direct(
        self, request_id: str, approved: bool = True, approver: Optional[str] = None
    ):
        """Directly invoke the approval handler (bypasses EventBus). Useful for tests or embedded controllers."""
        try:
            ev = Event(
                type=EventType.ACTION_APPROVAL_RESPONSE,
                data={
                    "request_id": request_id,
                    "approved": approved,
                    "approver": approver,
                },
            )
            # Call handler synchronously
            self._on_response(ev)
            return True
        except Exception as e:
            logger.debug(f"ActionApprovalManager: approve_direct failed: {e}")
            return False


# singleton
action_approval_manager = ActionApprovalManager()
