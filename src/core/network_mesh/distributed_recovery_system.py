#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Distributed Recovery Architecture Test
===========================================================
Testa a arquitetura de auto-recovery distribuÃ­do em clusters mÃºltiplos.
"""

import asyncio
import json
import time
import sys
import os
import logging
import argparse
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

# Adicionar src ao path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DistributedRecoveryTest")

class NodeStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"  # Performance baixa mas funcional
    FAILING = "failing"    # Problemas sÃ©rios
    OFFLINE = "offline"    # NÃ£o responsivo

class ServiceType(Enum):
    AI_AGENT = "ai_agent"
    VOICE_CONTROLLER = "voice_controller" 
    VISION_ENHANCER = "vision_enhancer"
    NEURAL_MEMORY = "neural_memory"
    HARDWARE_MANAGER = "hardware_manager"

@dataclass
class ClusterNode:
    """Representa um nÃ³ no cluster distribuÃ­do"""
    node_id: str
    location: str  # "us-east", "eu-west", "sa-east"
    status: NodeStatus
    services: List[ServiceType]
    cpu_usage: float
    memory_usage: float
    network_latency: float
    last_heartbeat: datetime
    capacity_score: float  # 0.0 a 1.0

@dataclass
class DistributedFailure:
    """Falha que afeta mÃºltiplos nÃ³s"""
    failure_id: str
    affected_nodes: Set[str]
    service_type: ServiceType
    severity_level: int  # 1-10
    is_cascading: bool   # Se a falha se espalha para outros nÃ³s
    estimated_recovery_time: int  # minutos

class DistributedRecoveryOrchestrator:
    """
    ðŸŒ ORCHESTRADOR DE RECOVERY DISTRIBUÃDO
    
    Gerencia recuperaÃ§Ã£o inteligente em clusters geo-distribuÃ­dos.
    CaracterÃ­sticas:
    - Consensus Algorithm para decisÃµes crÃ­ticas
    - Load Balancing dinÃ¢mico baseado em capacidade
    - Geo-replication para alta disponibilidade
    - Cascading failure prevention
    """
    
    def __init__(self):
        self.cluster_nodes: Dict[str, ClusterNode] = {}
        self.service_mapping: Dict[ServiceType, Set[str]] = {}  # serviÃ§o -> nÃ³s
        self.failure_history: List[DistributedFailure] = []
        self.consensus_threshold = 0.6  # 60% dos nÃ³s devem concordar
        self.max_migration_time = 300   # 5 minutos max para migrar serviÃ§o
        
        # Simular cluster inicial
        self._initialize_mock_cluster()
    
    def _initialize_mock_cluster(self):
        """Inicializa cluster simulado com 5 nÃ³s geo-distribuÃ­dos"""
        
        mock_nodes = [
            {
                "node_id": "us-east-01",
                "location": "Virginia, USA",
                "services": [ServiceType.AI_AGENT, ServiceType.NEURAL_MEMORY],
                "cpu": 25.0, "memory": 45.0, "latency": 12.0, "capacity": 0.85
            },
            {
                "node_id": "eu-west-02", 
                "location": "Frankfurt, Germany",
                "services": [ServiceType.VOICE_CONTROLLER, ServiceType.VISION_ENHANCER],
                "cpu": 15.0, "memory": 32.0, "latency": 8.0, "capacity": 0.92
            },
            {
                "node_id": "sa-east-03",
                "location": "SÃ£o Paulo, Brazil", 
                "services": [ServiceType.HARDWARE_MANAGER],
                "cpu": 40.0, "memory": 55.0, "latency": 25.0, "capacity": 0.70
            },
            {
                "node_id": "ap-southeast-04",
                "location": "Singapore",
                "services": [ServiceType.AI_AGENT],  # Backup AI
                "cpu": 20.0, "memory": 38.0, "latency": 15.0, "capacity": 0.88
            },
            {
                "node_id": "cloude-edge-05",
                "location": "Multi-Region Edge",
                "services": [],  # NÃ³ de emergÃªncia
                "cpu": 10.0, "memory": 25.0, "latency": 5.0, "capacity": 0.95
            }
        ]
        
        for node_data in mock_nodes:
            node = ClusterNode(
                node_id=node_data["node_id"],
                location=node_data["location"],
                status=NodeStatus.HEALTHY,
                services=node_data["services"],
                cpu_usage=node_data["cpu"],
                memory_usage=node_data["memory"],
                network_latency=node_data["latency"],
                last_heartbeat=datetime.now(),
                capacity_score=node_data["capacity"]
            )
            
            self.cluster_nodes[node.node_id] = node
            
            # Mapear serviÃ§os para nÃ³s
            for service in node_data["services"]:
                if service not in self.service_mapping:
                    self.service_mapping[service] = set()
                self.service_mapping[service].add(node_data["node_id"])
    
    async def detect_and_recover_failure(self, node_id: str, service: ServiceType) -> Dict:
        """
        ðŸš¨ DETECÃ‡ÃƒO E RECOVERY DISTRIBUÃDO
        
        Fluxo:
        1. Detecta falha em nÃ³ especÃ­fico
        2. Avalia impacto no cluster
        3. Executa consensus para estratÃ©gia
        4. Migra serviÃ§os para nÃ³ saudÃ¡vel
        5. Monitora recovery e ajusta
        """
        
        print(f"\nðŸš¨ FALHA DETECTADA: {service.value} no nÃ³ {node_id}")
        
        # 1. ANÃLISE DE IMPACTO
        impact = await self._analyze_failure_impact(node_id, service)
        print(f"ðŸ“Š Impacto analisado: {impact['severity']}/10 - NÃ³s afetados: {len(impact['affected_nodes'])}")
        
        # 2. CONSENSUS PARA ESTRATÃ‰GIA
        recovery_strategy = await self._build_recovery_consensus(node_id, service, impact)
        print(f"ðŸ—³ï¸ Consensus alcanÃ§ado: {recovery_strategy['strategy']} (confianÃ§a: {recovery_strategy['confidence']:.1%})")
        
        # 3. SELEÃ‡ÃƒO DE NÃ“ ALVO
        target_node = await self._select_optimal_target_node(service, impact)
        if not target_node:
            print("âŒ Nenhum nÃ³ disponÃ­vel para migration!")
            return {"success": False, "reason": "No available target node"}
        
        print(f"ðŸŽ¯ NÃ³ alvo selecionado: {target_node} ({self.cluster_nodes[target_node].location})")
        
        # 4. EXECUÃ‡ÃƒO DA MIGRAÃ‡ÃƒO
        migration_result = await self._execute_service_migration(
            service, 
            source_node=node_id,
            target_node=target_node,
            strategy=recovery_strategy
        )
        
        # 5. VERIFICAÃ‡ÃƒO PÃ“S-MIGRAÃ‡ÃƒO
        if migration_result["success"]:
            await self._verify_migration_success(target_node, service)
            print(f"âœ… MigraÃ§Ã£o bem-sucedida! {service.value} operando em {target_node}")
        else:
            print(f"âŒ MigraÃ§Ã£o falhou: {migration_result['error']}")
        
        return migration_result
    
    async def _analyze_failure_impact(self, node_id: str, service: ServiceType) -> Dict:
        """Analisa o impacto da falha no cluster"""
        
        affected_nodes = {node_id}
        severity = 3  # Base severity
        
        # Se Ã© um serviÃ§o crÃ­tico, aumenta severidade
        if service in [ServiceType.AI_AGENT, ServiceType.NEURAL_MEMORY]:
            severity += 3
        
        # Verifica se hÃ¡ outros nÃ³s com o mesmo serviÃ§o (redundÃ¢ncia)
        redundant_nodes = self.service_mapping.get(service, set()) - {node_id}
        if not redundant_nodes:
            severity += 4  # Sem redundÃ¢ncia = crÃ­tico
        
        # Simula cascading failure analysis
        if self.cluster_nodes[node_id].status == NodeStatus.FAILING:
            # Alto risco de cascading se nÃ³ estÃ¡ degradado hÃ¡ tempo
            severity += 2
            # Adiciona nÃ³s prÃ³ximos como potencialmente afetados
            for nid, node in self.cluster_nodes.items():
                if node.network_latency < 20 and nid != node_id:
                    affected_nodes.add(nid)
        
        return {
            "severity": min(severity, 10),
            "affected_nodes": affected_nodes,
            "has_redundancy": len(redundant_nodes) > 0,
            "redundant_nodes": redundant_nodes
        }
    
    async def _build_recovery_consensus(self, node_id: str, service: ServiceType, impact: Dict) -> Dict:
        """
        ðŸ—³ï¸ CONSENSUS ALGORITHM para estratÃ©gia de recovery
        
        Simula Raft Consensus onde nÃ³s votam na melhor estratÃ©gia.
        """
        
        available_nodes = [nid for nid, node in self.cluster_nodes.items() 
                          if node.status == NodeStatus.HEALTHY and nid != node_id]
        
        # Simular votaÃ§Ã£o
        votes = {}
        for voter_node in available_nodes:
            voter = self.cluster_nodes[voter_node]
            
            # Simula lÃ³gica de voto baseada em capacidade e localizaÃ§Ã£o
            if voter.capacity_score > 0.8:
                votes[voter_node] = "immediate_migration"
            elif voter.capacity_score > 0.6:
                votes[voter_node] = "gradual_migration"  
            else:
                votes[voter_node] = "wait_and_monitor"
        
        # Contar votos
        vote_count = {}
        for vote in votes.values():
            vote_count[vote] = vote_count.get(vote, 0) + 1
        
        # EstratÃ©gia vencedora
        winning_strategy = max(vote_count.items(), key=lambda x: x[1])
        confidence = winning_strategy[1] / len(votes) if votes else 0
        
        return {
            "strategy": winning_strategy[0],
            "confidence": confidence,
            "votes": votes
        }
    
    async def _select_optimal_target_node(self, service: ServiceType, impact: Dict) -> Optional[str]:
        """
        ðŸŽ¯ SELEÃ‡ÃƒO INTELIGENTE DE NÃ“ ALVO
        
        CritÃ©rios:
        - Capacidade disponÃ­vel (CPU, RAM)
        - LatÃªncia de rede
        - LocalizaÃ§Ã£o geogrÃ¡fica (nearness ao usuÃ¡rio)
        - Load balancing
        """
        
        candidates = []
        
        for node_id, node in self.cluster_nodes.items():
            if (node.status == NodeStatus.HEALTHY and 
                node.cpu_usage < 70 and 
                node.memory_usage < 80):
                
                # Calcular score total
                capacity_score = node.capacity_score
                latency_score = max(0, 1 - (node.network_latency / 100))
                load_score = max(0, 1 - (node.cpu_usage / 100))
                
                total_score = (capacity_score * 0.4 + 
                              latency_score * 0.3 + 
                              load_score * 0.3)
                
                candidates.append((node_id, total_score))
        
        if not candidates:
            return None
        
        # Retornar nÃ³ com maior score
        return max(candidates, key=lambda x: x[1])[0]
    
    async def _execute_service_migration(self, service: ServiceType, source_node: str, 
                                       target_node: str, strategy: Dict) -> Dict:
        """
        ðŸš€ EXECUÃ‡ÃƒO DE MIGRAÃ‡ÃƒO DE SERVIÃ‡O
        
        Simula migraÃ§Ã£o real com:
        - State backup
        - Service stop
        - State transfer
        - Service start
        - Verification
        """
        
        migration_steps = [
            "ðŸ“¦ Backup do estado do serviÃ§o...",
            "â¹ï¸ Parando serviÃ§o no nÃ³ source...",
            "ðŸ“¡ Transferindo estado para target...", 
            "ðŸš€ Iniciando serviÃ§o no nÃ³ target...",
            "âœ… Verificando healthcheck..."
        ]
        
        for i, step in enumerate(migration_steps):
            print(f"   [{i+1}/{len(migration_steps)}] {step}")
            await asyncio.sleep(0.5)  # Simula tempo de execuÃ§Ã£o
        
        # Atualizar mapping de serviÃ§os
        if service in self.service_mapping:
            self.service_mapping[service].discard(source_node)
            self.service_mapping[service].add(target_node)
        
        # Atualizar serviÃ§os do nÃ³
        if service in self.cluster_nodes[source_node].services:
            self.cluster_nodes[source_node].services.remove(service)
        self.cluster_nodes[target_node].services.append(service)
        
        return {
            "success": True,
            "migration_time": len(migration_steps) * 0.5,
            "source_node": source_node,
            "target_node": target_node
        }
    
    async def _verify_migration_success(self, target_node: str, service: ServiceType):
        """Verifica se migraÃ§Ã£o foi bem-sucedida"""
        # Simula health check
        await asyncio.sleep(1)
        print(f"ðŸ” Health check: {service.value} operacional em {target_node}")
    
    def get_cluster_status(self) -> Dict:
        """Retorna status completo do cluster"""
        
        total_nodes = len(self.cluster_nodes)
        healthy_nodes = len([n for n in self.cluster_nodes.values() if n.status == NodeStatus.HEALTHY])
        
        service_distribution = {}
        for service, nodes in self.service_mapping.items():
            service_distribution[service.value] = list(nodes)
        
        return {
            "total_nodes": total_nodes,
            "healthy_nodes": healthy_nodes,
            "uptime_percentage": (healthy_nodes / total_nodes * 100) if total_nodes > 0 else 0,
            "service_distribution": service_distribution,
            "geographic_spread": list(set([n.location for n in self.cluster_nodes.values()])),
            "total_failures_recovered": len(self.failure_history)
        }

# ============================================================================
# TESTE FUNCIONAL
# ============================================================================

async def distributed_recovery_demo():
    """DemonstaÃ§Ã£o completa do sistema distribuÃ­do - CONVERTIDA EM TESTE FUNCIONAL"""

    print("\nðŸŒ " + "="*60)
    print("    JARVIS DISTRIBUTED RECOVERY TEST")
    print("="*60 + "\n")

    orchestrator = DistributedRecoveryOrchestrator()

    # 1. STATUS INICIAL DO CLUSTER
    print("ðŸ“Š STATUS INICIAL DO CLUSTER:")
    status = orchestrator.get_cluster_status()
    print(f"   ðŸŒ NÃ³s totais: {status['total_nodes']}")
    print(f"   âœ… NÃ³s saudÃ¡veis: {status['healthy_nodes']} ({status['uptime_percentage']:.1f}% uptime)")
    print(f"   ðŸ—ºï¸ RegiÃµes: {', '.join(status['geographic_spread'])}")
    print(f"   âš¡ DistribuiÃ§Ã£o de serviÃ§os:")
    for service, nodes in status['service_distribution'].items():
        print(f"      â€¢ {service}: {nodes}")

    print("\n" + "="*60)

    # 2. SIMULAR FALHAS E RECOVERY - AGORA COMO TESTES FUNCIONAIS
    test_failures = [
        ("us-east-01", ServiceType.AI_AGENT, "ðŸ’¡ Sobrecarga na IA principal"),
        ("sa-east-03", ServiceType.HARDWARE_MANAGER, "ðŸ–¥ï¸ Hardware crÃ­tico offline"),
        ("eu-west-02", ServiceType.VISION_ENHANCER, "ðŸ‘ï¸ Sistema de visÃ£o falhou")
    ]

    successful_recoveries = 0

    for node_id, service, description in test_failures:
        print(f"\nðŸ§ª TESTE FUNCIONAL: {description}")
        print(f"   ðŸŽ¯ Falha em: {node_id} ({orchestrator.cluster_nodes[node_id].location})")

        recovery_result = await orchestrator.detect_and_recover_failure(node_id, service)

        if recovery_result["success"]:
            print(f"   ðŸŽ‰ âœ… Recovery bem-sucedido!")
            successful_recoveries += 1
        else:
            print(f"   ðŸ’” âŒ Recovery falhou: {recovery_result.get('reason', 'Erro desconhecido')}")

        print(f"   â±ï¸ Tempo de recovery: {recovery_result.get('migration_time', 0):.1f}s")
        print("-" * 60)

    # 3. RESULTADO DOS TESTES FUNCIONAIS
    success_rate = successful_recoveries / len(test_failures)

    print(f"\nðŸ“Š RESULTADO DOS TESTES FUNCIONAIS:")
    print(f"   âœ… Recoveries bem-sucedidas: {successful_recoveries}/{len(test_failures)}")
    print(".1%")

    if success_rate >= 0.6:
        print("   ðŸŽ‰ SISTEMA DISTRIBUÃDO APROVADO!")
        return True
    else:
        print("   âŒ SISTEMA DISTRIBUÃDO REPROVADO - Taxa de sucesso baixa")
        return False

class DistributedRecoveryTester:
    """
    Testador do sistema de recuperaÃ§Ã£o distribuÃ­da
    """

    def __init__(self):
        self.test_results: Dict[str, Any] = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {}
        }
        self.orchestrator = None

    async def run_distributed_tests(self) -> bool:
        """Executa testes do sistema distribuÃ­do"""
        print("ðŸŒ JARVIS Distributed Recovery Test Suite")
        print("=" * 60)

        self.orchestrator = DistributedRecoveryOrchestrator()

        tests = [
            ('cluster_initialization', self.test_cluster_initialization),
            ('failure_impact_analysis', self.test_failure_impact_analysis),
            ('consensus_algorithm', self.test_consensus_algorithm),
            ('service_migration', self.test_service_migration),
            ('recovery_scenarios', self.test_recovery_scenarios),
            ('performance_metrics', self.test_performance_metrics)
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\nðŸ” Executando teste distribuÃ­do: {test_name}")
            try:
                result = await test_func()
                self.test_results['tests'][test_name] = result

                if result['success']:
                    print(f"   âœ… {test_name}: PASSOU ({result.get('duration', 0):.2f}s)")
                    passed += 1
                else:
                    print(f"   âŒ {test_name}: FALHOU - {result.get('error', 'Erro desconhecido')}")

            except Exception as e:
                logger.error(f"Erro no teste {test_name}: {e}", exc_info=True)
                self.test_results['tests'][test_name] = {
                    'success': False,
                    'error': str(e),
                    'details': {}
                }
                print(f"   âŒ {test_name}: ERRO - {e}")

        # Resumo final
        self.test_results['summary'] = {
            'total_tests': total,
            'passed_tests': passed,
            'failed_tests': total - passed,
            'success_rate': passed / total if total > 0 else 0,
            'total_duration': sum(t.get('duration', 0) for t in self.test_results['tests'].values())
        }

        print(".1%")
        print(".2f")

        return passed == total

    async def test_cluster_initialization(self) -> Dict[str, Any]:
        """Testa inicializaÃ§Ã£o do cluster"""
        start_time = time.time()
        result = {'success': True, 'details': {}}

        try:
            status = self.orchestrator.get_cluster_status()

            # VerificaÃ§Ãµes bÃ¡sicas
            checks = {
                'has_nodes': status['total_nodes'] > 0,
                'has_healthy_nodes': status['healthy_nodes'] > 0,
                'has_geographic_spread': len(status['geographic_spread']) > 1,
                'has_service_distribution': len(status['service_distribution']) > 0
            }

            all_checks_passed = all(checks.values())

            result['details'] = {
                'cluster_status': status,
                'validation_checks': checks,
                'all_checks_passed': all_checks_passed
            }

            if not all_checks_passed:
                result['success'] = False
                result['error'] = f"VerificaÃ§Ãµes falharam: { [k for k, v in checks.items() if not v] }"

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        result['duration'] = time.time() - start_time
        return result

    async def test_failure_impact_analysis(self) -> Dict[str, Any]:
        """Testa anÃ¡lise de impacto de falhas"""
        start_time = time.time()
        result = {'success': True, 'details': {}}

        try:
            # Testar anÃ¡lise de impacto para diferentes cenÃ¡rios
            test_scenarios = [
                ("us-east-01", ServiceType.AI_AGENT),  # ServiÃ§o crÃ­tico
                ("sa-east-03", ServiceType.HARDWARE_MANAGER),  # ServiÃ§o Ãºnico
                ("eu-west-02", ServiceType.VOICE_CONTROLLER)  # ServiÃ§o normal
            ]

            impact_results = []
            for node_id, service in test_scenarios:
                impact = await self.orchestrator._analyze_failure_impact(node_id, service)
                impact_results.append({
                    'node': node_id,
                    'service': service.value,
                    'severity': impact['severity'],
                    'affected_nodes_count': len(impact['affected_nodes']),
                    'has_redundancy': impact['has_redundancy'],
                    'is_critical': impact['is_critical_service']
                })

            # Verificar se severidades fazem sentido
            critical_service = next(r for r in impact_results if r['is_critical'])
            normal_service = next(r for r in impact_results if not r['is_critical'])

            severity_logic_correct = critical_service['severity'] > normal_service['severity']

            result['details'] = {
                'impact_analysis_results': impact_results,
                'severity_logic_correct': severity_logic_correct,
                'scenarios_tested': len(test_scenarios)
            }

            if not severity_logic_correct:
                result['success'] = False
                result['error'] = "LÃ³gica de severidade incorreta"

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        result['duration'] = time.time() - start_time
        return result

    async def test_consensus_algorithm(self) -> Dict[str, Any]:
        """Testa algoritmo de consensus"""
        start_time = time.time()
        result = {'success': True, 'details': {}}

        try:
            # Testar consensus para diferentes cenÃ¡rios
            test_cases = [
                ("us-east-01", ServiceType.AI_AGENT, {"severity": 9}),  # Alta severidade
                ("eu-west-02", ServiceType.VOICE_CONTROLLER, {"severity": 4})  # Baixa severidade
            ]

            consensus_results = []
            for node_id, service, impact in test_cases:
                consensus = await self.orchestrator._build_recovery_consensus(node_id, service, impact)
                consensus_results.append({
                    'node': node_id,
                    'service': service.value,
                    'strategy': consensus['strategy'],
                    'confidence': consensus['confidence'],
                    'votes': consensus['votes']
                })

            # Verificar se estratÃ©gias sÃ£o apropriadas para severidade
            high_severity = next(r for r in consensus_results if r['node'] == "us-east-01")
            low_severity = next(r for r in consensus_results if r['node'] == "eu-west-02")

            strategy_logic_correct = (
                high_severity['strategy'] == "immediate_migration" and
                low_severity['strategy'] in ["load_balanced_migration", "gradual_transfer"]
            )

            result['details'] = {
                'consensus_results': consensus_results,
                'strategy_logic_correct': strategy_logic_correct,
                'average_confidence': sum(r['confidence'] for r in consensus_results) / len(consensus_results)
            }

            if not strategy_logic_correct:
                result['success'] = False
                result['error'] = "LÃ³gica de estratÃ©gia de consensus incorreta"

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        result['duration'] = time.time() - start_time
        return result

    async def test_service_migration(self) -> Dict[str, Any]:
        """Testa migraÃ§Ã£o de serviÃ§os"""
        start_time = time.time()
        result = {'success': True, 'details': {}}

        try:
            # Testar seleÃ§Ã£o de nÃ³ alvo
            service = ServiceType.AI_AGENT
            impact = {"affected_nodes": {"us-east-01"}}

            target_node = await self.orchestrator._select_optimal_target_node(service, impact)

            if not target_node:
                raise RuntimeError("Nenhum nÃ³ alvo encontrado")

            # Verificar se nÃ³ alvo Ã© vÃ¡lido
            target_valid = (
                target_node in self.orchestrator.cluster_nodes and
                target_node not in impact["affected_nodes"] and
                self.orchestrator.cluster_nodes[target_node].status == NodeStatus.HEALTHY
            )

            # Testar migraÃ§Ã£o simulada
            strategy = {"strategy": "immediate_migration", "confidence": 0.8}
            migration_result = await self.orchestrator._execute_service_migration(
                service, "us-east-01", target_node, strategy
            )

            result['details'] = {
                'target_node_selected': target_node,
                'target_node_valid': target_valid,
                'migration_attempted': True,
                'migration_success': migration_result['success'],
                'migration_time': migration_result['migration_time'],
                'service_mapping_updated': target_node in self.orchestrator.service_mapping.get(service, set())
            }

            if not target_valid:
                result['success'] = False
                result['error'] = "NÃ³ alvo invÃ¡lido selecionado"

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        result['duration'] = time.time() - start_time
        return result

    async def test_recovery_scenarios(self) -> Dict[str, Any]:
        """Testa cenÃ¡rios de recuperaÃ§Ã£o completos"""
        start_time = time.time()
        result = {'success': True, 'details': {}}

        try:
            # Testar cenÃ¡rios de recovery completos
            test_scenarios = [
                ("us-east-01", ServiceType.AI_AGENT, "AI principal sobrecarregada"),
                ("sa-east-03", ServiceType.HARDWARE_MANAGER, "Hardware crÃ­tico offline"),
                ("eu-west-02", ServiceType.VISION_ENHANCER, "Sistema de visÃ£o falhou")
            ]

            recovery_results = []
            for node_id, service, description in test_scenarios:
                recovery_result = await self.orchestrator.detect_and_recover_failure(node_id, service)
                recovery_results.append({
                    'node': node_id,
                    'service': service.value,
                    'description': description,
                    'success': recovery_result['success'],
                    'migration_time': recovery_result.get('migration_time', 0)
                })

            successful_recoveries = sum(1 for r in recovery_results if r['success'])
            success_rate = successful_recoveries / len(test_scenarios)

            result['details'] = {
                'recovery_scenarios': recovery_results,
                'successful_recoveries': successful_recoveries,
                'total_scenarios': len(test_scenarios),
                'success_rate': success_rate,
                'average_migration_time': sum(r['migration_time'] for r in recovery_results) / len(recovery_results)
            }

            # Recovery deve ter pelo menos 60% de sucesso
            if success_rate < 0.6:
                result['success'] = False
                result['error'] = f"Taxa de sucesso de recovery baixa: {success_rate:.1%}"

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        result['duration'] = time.time() - start_time
        return result

    async def test_performance_metrics(self) -> Dict[str, Any]:
        """Testa mÃ©tricas de performance"""
        start_time = time.time()
        result = {'success': True, 'details': {}}

        try:
            # Medir performance de operaÃ§Ãµes crÃ­ticas
            import time

            # Tempo para obter status do cluster
            start_status = time.time()
            status = self.orchestrator.get_cluster_status()
            status_time = time.time() - start_status

            # Tempo para anÃ¡lise de impacto
            start_impact = time.time()
            impact = await self.orchestrator._analyze_failure_impact("us-east-01", ServiceType.AI_AGENT)
            impact_time = time.time() - start_impact

            # Verificar performance aceitÃ¡vel (< 2 segundos para operaÃ§Ãµes crÃ­ticas)
            acceptable_performance = status_time < 2.0 and impact_time < 2.0

            result['details'] = {
                'cluster_status_time': status_time,
                'impact_analysis_time': impact_time,
                'acceptable_performance': acceptable_performance,
                'performance_metrics': {
                    'status_time_ms': status_time * 1000,
                    'impact_time_ms': impact_time * 1000
                }
            }

            if not acceptable_performance:
                result['success'] = False
                result['error'] = "Performance abaixo do aceitÃ¡vel (>2s para operaÃ§Ãµes crÃ­ticas)"

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        result['duration'] = time.time() - start_time
        return result

    def save_results(self, output_file: str) -> bool:
        """Salva os resultados em arquivo JSON"""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False, default=str)

            print(f"ðŸ’¾ Resultados salvos em: {output_path}")
            return True

        except Exception as e:
            print(f"âŒ Erro ao salvar resultados: {e}")
            return False

    def print_summary(self):
        """Imprime resumo dos resultados"""
        summary = self.test_results.get('summary', {})

        print("\nðŸ“Š RESUMO DOS TESTES DISTRIBUÃDOS:")
        print("-" * 50)
        print(f"   Total de testes: {summary.get('total_tests', 0)}")
        print(f"   Testes aprovados: {summary.get('passed_tests', 0)}")
        print(f"   Testes reprovados: {summary.get('failed_tests', 0)}")
        print(".1%")
        print(".2f")

        if summary.get('failed_tests', 0) > 0:
            print("\nâŒ TESTES QUE FALHARAM:")
            for test_name, test_result in self.test_results.get('tests', {}).items():
                if not test_result.get('success', False):
                    error = test_result.get('error', 'Erro desconhecido')
                    print(f"   â€¢ {test_name}: {error}")

async def run_distributed_tests(output_file: Optional[str] = None, verbose: bool = False) -> bool:
    """
    Executa testes do sistema de recuperaÃ§Ã£o distribuÃ­da

    Args:
        output_file: Arquivo para salvar resultados (opcional)
        verbose: Modo verboso

    Returns:
        True se todos os testes passaram
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    tester = DistributedRecoveryTester()

    try:
        success = await tester.run_distributed_tests()

        tester.print_summary()

        if output_file:
            tester.save_results(output_file)

        return success

    except Exception as e:
        logger.error(f"Erro durante testes distribuÃ­dos: {e}")
        return False

def main():
    """FunÃ§Ã£o principal"""
    parser = argparse.ArgumentParser(
        description="Distributed Recovery Test - JARVIS 5.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

# Executar todos os testes distribuÃ­dos
python src/core/network_mesh/distributed_recovery_system.py

# Salvar resultados em arquivo
python src/core/network_mesh/distributed_recovery_system.py --output distributed_test_results.json

# Modo verboso
python src/core/network_mesh/distributed_recovery_system.py --verbose
        """
    )

    parser.add_argument('--output', '-o', help='Arquivo para salvar resultados dos testes')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso com debug')

    args = parser.parse_args()

    success = asyncio.run(run_distributed_tests(args.output, args.verbose))

    if success:
        print("\nðŸŽ‰ Todos os testes distribuÃ­dos passaram!")
        sys.exit(0)
    else:
        print("\nâŒ Alguns testes falharam. Verifique os logs acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()
