"""
AlertManager - Sistema de alertas inteligentes para JARVIS 5.0
Gerencia alertas, notificações e respostas automáticas.
"""

import json
import logging
import time
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Awaitable
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Níveis de severidade para alertas."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Status possíveis para alertas."""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class AlertRule:
    """Regra para geração de alertas."""

    rule_id: str
    name: str
    description: str
    condition: Callable[[Dict[str, Any]], bool]
    severity: AlertSeverity
    cooldown_seconds: int = 300  # 5 minutos
    auto_resolve: bool = False
    actions: List[Callable[[Dict[str, Any]], Awaitable[None]]] = None

    def __post_init__(self):
        if self.actions is None:
            self.actions = []


@dataclass
class Alert:
    """Representa um alerta do sistema."""

    alert_id: str
    rule_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    created_at: float
    updated_at: float
    resolved_at: Optional[float] = None
    acknowledged_at: Optional[float] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    labels: Dict[str, str] = None
    annotations: Dict[str, Any] = None
    value: Any = None
    threshold: Any = None

    def __post_init__(self):
        if self.labels is None:
            self.labels = {}
        if self.annotations is None:
            self.annotations = {}

    def acknowledge(self, by: str = "system"):
        """Marca o alerta como reconhecido."""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_at = time.time()
        self.acknowledged_by = by
        self.updated_at = time.time()

    def resolve(self, by: str = "system"):
        """Resolve o alerta."""
        self.status = AlertStatus.RESOLVED
        self.resolved_at = time.time()
        self.resolved_by = by
        self.updated_at = time.time()

    def is_expired(self, max_age_seconds: int = 86400) -> bool:
        """Verifica se o alerta expirou."""
        return (time.time() - self.created_at) > max_age_seconds


class AlertManager:
    """
    Gerenciador de alertas inteligentes com regras automáticas e notificações.
    """

    def __init__(self, alert_dir: Path = None, max_alerts: int = 1000):
        self.alert_dir = alert_dir or Path("data/logs/alerts")
        self.alert_dir.mkdir(parents=True, exist_ok=True)
        self.max_alerts = max_alerts

        # Armazenamento de alertas
        self.active_alerts: Dict[str, Alert] = {}
        self.resolved_alerts: Dict[str, Alert] = {}
        self.alert_rules: Dict[str, AlertRule] = {}

        # Configurações de notificação
        self.notification_channels: Dict[str, Callable] = {}
        self.email_config: Dict[str, Any] = {}

        # Estado interno
        self.last_check_times: Dict[str, float] = {}

        # Inicializa regras padrão
        self._init_default_rules()

    def _init_default_rules(self):
        """Inicializa regras de alerta padrão."""

        # Regra para alta utilização de CPU
        self.add_rule(
            AlertRule(
                rule_id="high_cpu_usage",
                name="High CPU Usage",
                description="CPU usage above 90% for extended period",
                condition=lambda metrics: metrics.get("cpu_percent", 0) > 90,
                severity=AlertSeverity.HIGH,
                cooldown_seconds=300,
            )
        )

        # Regra para alta utilização de memória
        self.add_rule(
            AlertRule(
                rule_id="high_memory_usage",
                name="High Memory Usage",
                description="Memory usage above 90%",
                condition=lambda metrics: metrics.get("memory_percent", 0) > 90,
                severity=AlertSeverity.HIGH,
                cooldown_seconds=300,
            )
        )

        # Regra para erros críticos
        self.add_rule(
            AlertRule(
                rule_id="critical_error",
                name="Critical Error Detected",
                description="Critical error in system logs",
                condition=lambda data: data.get("level") == "CRITICAL"
                or data.get("error_type") == "critical",
                severity=AlertSeverity.CRITICAL,
                cooldown_seconds=60,
            )
        )

        # Regra para falha de serviço
        self.add_rule(
            AlertRule(
                rule_id="service_failure",
                name="Service Failure",
                description="Core service has failed",
                condition=lambda data: data.get("service_status") == "failed",
                severity=AlertSeverity.CRITICAL,
                cooldown_seconds=30,
            )
        )

    def add_rule(self, rule: AlertRule):
        """
        Adiciona uma nova regra de alerta.

        Args:
            rule: Regra a ser adicionada
        """
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.name} ({rule.rule_id})")

    def remove_rule(self, rule_id: str):
        """
        Remove uma regra de alerta.

        Args:
            rule_id: ID da regra
        """
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")

    async def check_rules(
        self, metrics: Dict[str, Any], context: Dict[str, Any] = None
    ):
        """
        Verifica todas as regras contra as métricas fornecidas.

        Args:
            metrics: Métricas do sistema
            context: Contexto adicional
        """
        context = context or {}
        current_time = time.time()

        for rule in self.alert_rules.values():
            # Verifica cooldown
            last_check = self.last_check_times.get(rule.rule_id, 0)
            if (current_time - last_check) < rule.cooldown_seconds:
                continue

            try:
                # Combina métricas e contexto
                check_data = {**metrics, **context}

                # Verifica condição
                if rule.condition(check_data):
                    await self._trigger_alert(rule, check_data)
                    self.last_check_times[rule.rule_id] = current_time

            except Exception as e:
                logger.error(f"Error checking rule {rule.rule_id}: {e}")

    async def _trigger_alert(self, rule: AlertRule, data: Dict[str, Any]):
        """
        Dispara um alerta baseado na regra.

        Args:
            rule: Regra que disparou
            data: Dados que ativaram a regra
        """
        # Verifica se já existe um alerta ativo para esta regra
        existing_alert = None
        for alert in self.active_alerts.values():
            if alert.rule_id == rule.rule_id and alert.status == AlertStatus.ACTIVE:
                existing_alert = alert
                break

        if existing_alert:
            # Atualiza alerta existente
            existing_alert.updated_at = time.time()
            existing_alert.value = data
            logger.info(f"Updated existing alert: {existing_alert.title}")
        else:
            # Cria novo alerta
            alert_id = f"{rule.rule_id}_{int(time.time())}"
            alert = Alert(
                alert_id=alert_id,
                rule_id=rule.rule_id,
                title=rule.name,
                description=rule.description,
                severity=rule.severity,
                status=AlertStatus.ACTIVE,
                created_at=time.time(),
                updated_at=time.time(),
                value=data,
                labels={"rule": rule.rule_id, "severity": rule.severity.value},
                annotations={"trigger_data": data},
            )

            self.active_alerts[alert_id] = alert
            await self._notify_alert(alert)

            # Executa ações automáticas
            for action in rule.actions:
                try:
                    await action(data)
                except Exception as e:
                    logger.error(f"Error executing alert action: {e}")

            logger.warning(
                f"Triggered new alert: {alert.title} (severity: {alert.severity.value})"
            )

    async def _notify_alert(self, alert: Alert):
        """
        Notifica sobre um novo alerta através dos canais configurados.

        Args:
            alert: Alerta a ser notificado
        """
        for channel_name, channel_func in self.notification_channels.items():
            try:
                await channel_func(alert)
            except Exception as e:
                logger.error(f"Error sending notification via {channel_name}: {e}")

    def acknowledge_alert(self, alert_id: str, by: str = "system"):
        """
        Reconhece um alerta.

        Args:
            alert_id: ID do alerta
            by: Quem reconheceu
        """
        alert = self.active_alerts.get(alert_id)
        if alert:
            alert.acknowledge(by)
            logger.info(f"Alert {alert_id} acknowledged by {by}")

    def resolve_alert(self, alert_id: str, by: str = "system"):
        """
        Resolve um alerta.

        Args:
            alert_id: ID do alerta
            by: Quem resolveu
        """
        alert = self.active_alerts.get(alert_id)
        if alert:
            alert.resolve(by)
            # Move para resolved
            self.resolved_alerts[alert_id] = alert
            del self.active_alerts[alert_id]

            # Salva alerta
            self._save_alert(alert)

            # Mantém limite
            if len(self.resolved_alerts) > self.max_alerts:
                oldest_id = min(
                    self.resolved_alerts.keys(),
                    key=lambda x: self.resolved_alerts[x].created_at,
                )
                del self.resolved_alerts[oldest_id]

            logger.info(f"Alert {alert_id} resolved by {by}")

    def _save_alert(self, alert: Alert):
        """Salva um alerta em arquivo."""
        try:
            alert_file = self.alert_dir / f"{alert.alert_id}.json"
            with open(alert_file, "w", encoding="utf-8") as f:
                json.dump(asdict(alert), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save alert {alert.alert_id}: {e}")

    def get_active_alerts(self, severity: AlertSeverity = None) -> List[Alert]:
        """
        Retorna alertas ativos.

        Args:
            severity: Filtrar por severidade

        Returns:
            Lista de alertas ativos
        """
        alerts = list(self.active_alerts.values())
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return sorted(alerts, key=lambda x: x.created_at, reverse=True)

    def get_resolved_alerts(self, limit: int = 100) -> List[Alert]:
        """
        Retorna alertas resolvidos.

        Args:
            limit: Número máximo de alertas

        Returns:
            Lista de alertas resolvidos
        """
        alerts = list(self.resolved_alerts.values())
        return sorted(alerts, key=lambda x: x.created_at, reverse=True)[:limit]

    def get_alert_summary(self) -> Dict[str, Any]:
        """Retorna um resumo dos alertas."""
        active_by_severity = {}
        for severity in AlertSeverity:
            active_by_severity[severity.value] = len(
                [a for a in self.active_alerts.values() if a.severity == severity]
            )

        return {
            "total_active": len(self.active_alerts),
            "total_resolved": len(self.resolved_alerts),
            "active_by_severity": active_by_severity,
            "rules_count": len(self.alert_rules),
        }

    # Métodos de configuração de notificações

    def add_notification_channel(self, name: str, channel_func: Callable):
        """
        Adiciona um canal de notificação.

        Args:
            name: Nome do canal
            channel_func: Função assíncrona que recebe um Alert
        """
        self.notification_channels[name] = channel_func
        logger.info(f"Added notification channel: {name}")

    def configure_email(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str,
        to_emails: List[str],
    ):
        """
        Configura notificações por email.

        Args:
            smtp_server: Servidor SMTP
            smtp_port: Porta SMTP
            username: Usuário SMTP
            password: Senha SMTP
            from_email: Email remetente
            to_emails: Lista de emails destinatários
        """
        self.email_config = {
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "username": username,
            "password": password,
            "from_email": from_email,
            "to_emails": to_emails,
        }

        # Adiciona canal de email
        self.add_notification_channel("email", self._send_email_notification)

    async def _send_email_notification(self, alert: Alert):
        """Envia notificação por email."""
        if not self.email_config:
            return

        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_config["from_email"]
            msg["To"] = ", ".join(self.email_config["to_emails"])
            msg["Subject"] = (
                f"JARVIS Alert: {alert.title} ({alert.severity.value.upper()})"
            )

            body = f"""
JARVIS Alert Notification

Title: {alert.title}
Severity: {alert.severity.value.upper()}
Status: {alert.status.value}
Created: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert.created_at))}

Description: {alert.description}

Labels: {alert.labels}
Annotations: {alert.annotations}

Value: {alert.value}
Threshold: {alert.threshold}
            """

            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(
                self.email_config["smtp_server"], self.email_config["smtp_port"]
            )
            server.starttls()
            server.login(self.email_config["username"], self.email_config["password"])
            text = msg.as_string()
            server.sendmail(
                self.email_config["from_email"], self.email_config["to_emails"], text
            )
            server.quit()

            logger.info(f"Sent email notification for alert {alert.alert_id}")

        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")


# Singleton instance
alert_manager = AlertManager()
