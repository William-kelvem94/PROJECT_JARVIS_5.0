#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for JARVIS 5.0 Evolution Layer
Tests the self-healing system components
"""

import sys
import os
import asyncio
import tempfile
import shutil
from pathlib import Path
import sqlite3
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from src.evolution.knowledge_db import KnowledgeDatabase
from src.evolution.self_observer import SelfObserver
from src.evolution.auto_healer import AutoHealer
from src.evolution.safe_executor import SafeExecutor
from src.evolution.evolution_manager import EvolutionManager


class TestKnowledgeDatabase:
    """Tests for the Knowledge Database component"""

    def setup_method(self):
        """Setup test database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_knowledge.db"
        self.db = KnowledgeDatabase(self.db_path)

    def teardown_method(self):
        """Cleanup test database"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_database_initialization(self):
        """Test that database and tables are created properly"""
        assert self.db_path.exists()
        
        # Check tables exist
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('problems', 'solutions', 'human_feedback')
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
        assert 'problems' in tables
        assert 'solutions' in tables
        assert 'human_feedback' in tables

    def test_record_problem(self):
        """Test recording a new problem"""
        problem_id = self.db.record_problem(
            hash_value="test_hash_123",
            module="test_module",
            description="Test problem",
            severity="high"
        )
        
        assert problem_id > 0
        
        # Verify problem was recorded
        problem = self.db.get_problem_by_hash("test_hash_123")
        assert problem is not None
        assert problem['module'] == "test_module"
        assert problem['description'] == "Test problem"
        assert problem['severity'] == "high"
        assert problem['occurrences'] == 1

    def test_problem_occurrence_increment(self):
        """Test that recording the same problem increments occurrence count"""
        hash_value = "test_hash_increment"
        
        # Record first time
        id1 = self.db.record_problem(hash_value, "module", "Test", "low")
        problem1 = self.db.get_problem_by_hash(hash_value)
        assert problem1['occurrences'] == 1
        
        # Record again
        id2 = self.db.record_problem(hash_value, "module", "Test", "low")
        problem2 = self.db.get_problem_by_hash(hash_value)
        
        assert id1 == id2  # Same problem ID
        assert problem2['occurrences'] == 2  # Incremented

    def test_record_solution(self):
        """Test recording a solution"""
        # First record a problem
        problem_hash = "problem_for_solution"
        self.db.record_problem(problem_hash, "test_module", "Test problem", "medium")
        
        # Record solution
        solution_id = self.db.record_solution(
            problem_hash=problem_hash,
            action_type="code",
            description="Fixed the bug",
            success=True,
            files_modified=["file1.py", "file2.py"],
            impact_score=0.9,
            execution_time_ms=150
        )
        
        assert solution_id > 0
        
        # Verify solution was recorded
        solutions = self.db.get_successful_solutions(problem_hash)
        assert len(solutions) == 1
        assert solutions[0]['action_type'] == "code"
        assert solutions[0]['success'] == 1
        assert solutions[0]['impact_score'] == 0.9

    def test_get_successful_solutions(self):
        """Test retrieving successful solutions"""
        problem_hash = "multi_solution_problem"
        self.db.record_problem(problem_hash, "module", "Problem", "high")
        
        # Record multiple solutions
        self.db.record_solution(problem_hash, "code", "Solution 1", True, impact_score=0.8)
        self.db.record_solution(problem_hash, "code", "Solution 2", False, impact_score=0.0)
        self.db.record_solution(problem_hash, "config", "Solution 3", True, impact_score=0.95)
        
        # Get successful solutions
        solutions = self.db.get_successful_solutions(problem_hash, limit=5)
        
        # Should only return successful ones, ordered by impact_score
        assert len(solutions) == 2
        assert solutions[0]['impact_score'] == 0.95  # Highest first
        assert solutions[1]['impact_score'] == 0.8

    def test_human_feedback(self):
        """Test adding human feedback"""
        problem_hash = "feedback_test"
        self.db.record_problem(problem_hash, "module", "Problem", "low")
        solution_id = self.db.record_solution(problem_hash, "code", "Fix", True)
        
        # Add feedback
        feedback_id = self.db.add_human_feedback(
            solution_id=solution_id,
            feedback="positive",
            comment="Great fix!"
        )
        
        assert feedback_id > 0

    def test_statistics(self):
        """Test statistics generation"""
        # Add some data
        self.db.record_problem("h1", "mod1", "P1", "low")
        self.db.record_problem("h2", "mod1", "P2", "high")
        self.db.record_problem("h3", "mod2", "P3", "medium")
        
        self.db.record_solution("h1", "code", "S1", True)
        self.db.record_solution("h2", "config", "S2", False)
        self.db.record_solution("h3", "code", "S3", True)
        
        stats = self.db.get_statistics()
        
        assert stats['total_problems'] == 3
        assert stats['total_solutions'] == 3
        assert stats['success_rate'] > 0
        assert len(stats['top_affected_modules']) > 0


class TestSelfObserver:
    """Tests for the Self Observer component"""

    @pytest.mark.asyncio
    async def test_observer_initialization(self):
        """Test that observer can be initialized"""
        observer = SelfObserver()
        assert observer is not None
        assert not observer.running

    @pytest.mark.asyncio
    async def test_hardware_metrics_collection(self):
        """Test collecting hardware metrics"""
        observer = SelfObserver()
        metrics = observer._collect_hardware_metrics()
        
        assert 'cpu_percent' in metrics
        assert 'memory_percent' in metrics
        assert isinstance(metrics['cpu_percent'], (int, float))

    @pytest.mark.asyncio
    async def test_config_health_check(self):
        """Test configuration health checking"""
        observer = SelfObserver()
        health = observer._check_config_integrity()
        
        assert 'missing_keys' in health
        assert 'invalid_paths' in health
        assert isinstance(health['missing_keys'], list)

    @pytest.mark.asyncio
    async def test_full_report_generation(self):
        """Test generating a full system report"""
        observer = SelfObserver()
        report = await observer.generate_full_report()
        
        assert 'timestamp' in report
        assert 'metrics' in report
        assert 'code_health' in report
        assert 'config_health' in report
        assert 'operational_health' in report
        assert 'recent_errors' in report


class TestAutoHealer:
    """Tests for the Auto Healer component"""

    def test_healer_initialization(self):
        """Test healer can be initialized"""
        healer = AutoHealer()
        assert healer is not None
        assert not healer.running

    def test_error_hashing(self):
        """Test error hash generation"""
        healer = AutoHealer()
        error1 = {"component": "test", "message": "Error"}
        error2 = {"component": "test", "message": "Error"}
        error3 = {"component": "other", "message": "Error"}
        
        hash1 = healer._hash_error(error1)
        hash2 = healer._hash_error(error2)
        hash3 = healer._hash_error(error3)
        
        assert hash1 == hash2  # Same error -> same hash
        assert hash1 != hash3  # Different error -> different hash

    def test_problem_identification(self):
        """Test identifying problems from report"""
        healer = AutoHealer()
        report = {
            "config_health": {
                "missing_keys": ["test.key"]
            },
            "code_health": {
                "bare_excepts": [
                    {"file": "test.py", "line": 42}
                ]
            },
            "recent_errors": [
                {"component": "test", "message": "RuntimeError"}
            ]
        }
        
        problems = healer._identify_problems(report)
        
        assert len(problems) > 0
        assert any(p['type'] == 'config_missing' for p in problems)
        assert any(p['type'] == 'code_quality' for p in problems)
        assert any(p['type'] == 'runtime_error' for p in problems)


class TestSafeExecutor:
    """Tests for the Safe Executor component"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "test_file.py"
        self.test_file.write_text("# Test file\nprint('hello')\n")

    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_executor_initialization(self):
        """Test executor can be initialized"""
        executor = SafeExecutor()
        assert executor is not None
        assert not executor.running

    def test_backup_creation(self):
        """Test file backup functionality"""
        executor = SafeExecutor()
        backup_path = executor._create_backup(self.test_file)
        
        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.read_text() == self.test_file.read_text()

    def test_validation_syntax_check(self):
        """Test Python syntax validation"""
        executor = SafeExecutor()
        
        # Valid Python file
        valid_file = Path(self.temp_dir) / "valid.py"
        valid_file.write_text("def test():\n    return 42\n")
        assert executor._validate_change(valid_file)
        
        # Invalid Python file
        invalid_file = Path(self.temp_dir) / "invalid.py"
        invalid_file.write_text("def test(\n    invalid syntax\n")
        assert not executor._validate_change(invalid_file)


class TestEvolutionManager:
    """Tests for the Evolution Manager"""

    @pytest.mark.asyncio
    async def test_manager_initialization(self):
        """Test manager can be initialized"""
        manager = EvolutionManager()
        assert manager is not None
        assert not manager.running

    @pytest.mark.asyncio
    async def test_status_report(self):
        """Test status reporting"""
        manager = EvolutionManager()
        status = manager.get_status()
        
        assert 'running' in status
        assert 'auto_heal_enabled' in status
        assert 'components' in status
        assert not status['running']  # Not started yet

    def test_auto_heal_toggle(self):
        """Test enabling/disabling auto-heal"""
        manager = EvolutionManager()
        
        # Enable
        manager.enable_auto_heal()
        assert manager.auto_heal_enabled
        
        # Disable
        manager.disable_auto_heal()
        assert not manager.auto_heal_enabled


def test_integration_imports():
    """Test that all components can be imported from the package"""
    from src.evolution import (
        evolution_manager,
        self_observer,
        auto_healer,
        safe_executor,
        knowledge_db
    )
    
    assert evolution_manager is not None
    assert self_observer is not None
    assert auto_healer is not None
    assert safe_executor is not None
    assert knowledge_db is not None


if __name__ == '__main__':
    print("=== Running JARVIS Evolution Layer Tests ===")
    pytest.main([__file__, '-v'])
