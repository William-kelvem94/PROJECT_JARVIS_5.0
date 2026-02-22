"""
DocumentationGenerator - Gerador automático de documentação para JARVIS 5.0
Gera documentação técnica, READMEs e guias automaticamente.
"""

import ast
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class CodeEntity:
    """Entidade de código (classe, função, método)."""

    name: str
    type: str  # 'class', 'function', 'method', 'module'
    file_path: Path
    line_number: int
    docstring: Optional[str] = None
    signature: Optional[str] = None
    dependencies: List[str] = None
    complexity: Optional[int] = None
    test_coverage: Optional[float] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class DocumentationSection:
    """Seção de documentação."""

    title: str
    content: str
    level: int = 1  # Nível do cabeçalho (1-6)
    subsections: List["DocumentationSection"] = None

    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []


class DocumentationGenerator:
    """
    Gerador automático de documentação técnica e READMEs.
    """

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.docs_dir = self.project_root / "docs"
        self.docs_dir.mkdir(exist_ok=True)

    def generate_api_documentation(self, source_dir: Path = None) -> str:
        """
        Gera documentação da API analisando código fonte.

        Args:
            source_dir: Diretório fonte (padrão: src)

        Returns:
            Documentação em formato Markdown
        """
        source_dir = source_dir or self.project_root / "src"

        entities = self._analyze_source_code(source_dir)

        # Organiza por módulos
        modules = {}
        for entity in entities:
            module_name = self._get_module_name(entity.file_path)
            if module_name not in modules:
                modules[module_name] = []
            modules[module_name].append(entity)

        # Gera documentação
        doc = [
            "# API Documentation\n",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        ]

        for module_name, module_entities in sorted(modules.items()):
            doc.append(f"## Module: {module_name}\n")

            # Classes
            classes = [e for e in module_entities if e.type == "class"]
            if classes:
                doc.append("### Classes\n")
                for cls in classes:
                    doc.append(self._format_entity_documentation(cls))

            # Functions
            functions = [e for e in module_entities if e.type == "function"]
            if functions:
                doc.append("### Functions\n")
                for func in functions:
                    doc.append(self._format_entity_documentation(func))

        return "\n".join(doc)

    def generate_readme(self, project_info: Dict[str, Any] = None) -> str:
        """
        Gera README.md automático baseado na estrutura do projeto.

        Args:
            project_info: Informações adicionais do projeto

        Returns:
            Conteúdo do README
        """
        project_info = project_info or {}

        # Análise básica do projeto
        project_name = project_info.get("name", "JARVIS 5.0")
        description = project_info.get(
            "description", "Advanced AI Assistant System")

        # Estrutura de seções
        sections = [
            DocumentationSection(
                "Project Title", f"# {project_name}\n\n{description}\n"
            ),
            self._generate_features_section(),
            self._generate_installation_section(),
            self._generate_usage_section(),
            self._generate_architecture_section(),
            self._generate_api_section(),
            self._generate_testing_section(),
            self._generate_deployment_section(),
            self._generate_contributing_section(),
            self._generate_license_section(),
        ]

        # Gera README
        readme_content = []
        for section in sections:
            readme_content.append(self._render_section(section))

        return "\n".join(readme_content)

    def generate_architecture_documentation(self) -> str:
        """
        Gera documentação da arquitetura do sistema.

        Returns:
            Documentação da arquitetura
        """
        doc = [
            "# System Architecture\n",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        ]

        # Componentes principais
        components = {
            "Core System": [
                "SecurityManager - Gerenciamento de segurança e validação",
                "ConfigManager - Configurações hierárquicas",
                "GlobalEventBus - Comunicação entre componentes",
                "ActionController - Controle de ações do sistema",
            ],
            "Evolution Layer": [
                "SelfObserver - Auto-observação e métricas",
                "AdvancedMetricsCollector - Coleta avançada de métricas",
                "TraceManager - Rastreamento distribuído",
                "AlertManager - Sistema de alertas inteligentes",
                "AutoHealer - Auto-correção de problemas",
            ],
            "Utilities": [
                "LazyLoader - Carregamento lazy de módulos",
                "MemoryManager - Gerenciamento de memória",
                "AsyncRunner - Executor assíncrono",
                "BaseHUD - Interface unificada",
            ],
            "Testing & Quality": [
                "JarvisTestSuite - Suite completa de testes",
                "PerformanceTestSuite - Testes de performance",
                "DocumentationGenerator - Geração automática de docs",
            ],
        }

        for component_group, component_list in components.items():
            doc.append(f"## {component_group}\n")
            for component in component_list:
                doc.append(f"- {component}")
            doc.append("")

        # Diagrama de arquitetura (simplificado)
        doc.append("## Architecture Diagram\n")
        doc.append("```\n")
        doc.append("┌─────────────────┐    ┌─────────────────┐")
        doc.append("│   User Interface│    │  Core System    │")
        doc.append("│   (HUD/BaseHUD) │◄──►│                 │")
        doc.append("└─────────────────┘    │ • Security      │")
        doc.append("                       │ • Configuration │")
        doc.append("                       │ • Event Bus     │")
        doc.append("                       └─────────────────┘")
        doc.append("                                ▲")
        doc.append("                                │")
        doc.append("                       ┌─────────────────┐")
        doc.append("                       │ Evolution Layer │")
        doc.append("                       │                 │")
        doc.append("                       │ • Self-Observer │")
        doc.append("                       │ • Auto-Healing  │")
        doc.append("                       │ • Metrics       │")
        doc.append("                       │ • Tracing       │")
        doc.append("                       └─────────────────┘")
        doc.append("```\n")

        return "\n".join(doc)

    def generate_deployment_guide(self) -> str:
        """
        Gera guia de deployment.

        Returns:
            Guia de deployment
        """
        guide = [
            "# Deployment Guide\n",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        ]

        guide.extend(["## Prerequisites\n",
                      "- Python 3.8+\n",
                      "- pip\n",
                      "- Virtual environment (recommended)\n",
                      "- Git\n\n",
                      "## Local Development Setup\n",
                      "```bash\n",
                      "# Clone the repository\n",
                      "git clone <repository-url>\n",
                      "cd PROJECT_JARVIS_5.0\n\n",
                      "# Create virtual environment\n",
                      "python -m venv venv\n",
                      "source venv/bin/activate  # On Windows: venv\\Scripts\\activate\n\n",
                      "# Install dependencies\n",
                      "pip install -r requirements.txt\n\n",
                      "# Run tests\n",
                      "python -m pytest tests/\n\n",
                      "# Start the system\n",
                      "python main.py\n",
                      "```\n\n",
                      "## Production Deployment\n",
                      "### Option 1: Docker Deployment\n",
                      "```bash\n",
                      "# Build Docker image\n",
                      "docker build -t jarvis-5.0 .\n\n",
                      "# Run container\n",
                      "docker run -d --name jarvis jarvis-5.0\n",
                      "```\n\n",
                      "### Option 2: Systemd Service\n",
                      "```bash\n",
                      "# Create systemd service file\n",
                      "sudo nano /etc/systemd/system/jarvis.service\n\n",
                      "# Service content:\n",
                      "[Unit]\n",
                      "Description=JARVIS 5.0 AI Assistant\n",
                      "After=network.target\n\n",
                      "[Service]\n",
                      "Type=simple\n",
                      "User=jarvis\n",
                      "WorkingDirectory=/opt/jarvis\n",
                      "ExecStart=/opt/jarvis/venv/bin/python main.py\n",
                      "Restart=always\n\n",
                      "[Install]\n",
                      "WantedBy=multi-user.target\n\n",
                      "# Enable and start service\n",
                      "sudo systemctl enable jarvis\n",
                      "sudo systemctl start jarvis\n",
                      "```\n\n",
                      "## Configuration\n",
                      "Copy and modify configuration files:\n",
                      "```bash\n",
                      "cp config/*.yaml config/production/\n",
                      "nano config/production/*.yaml  # Edit for production\n",
                      "```\n\n",
                      "## Monitoring\n",
                      "- Check logs: `tail -f data/logs/*.txt`\n",
                      "- Monitor processes: `ps aux | grep python`\n",
                      "- System resources: `htop` or `top`\n\n",
                      "## Backup\n",
                      "```bash\n",
                      "# Backup data directory\n",
                      "tar -czf backup_$(date +%Y%m%d).tar.gz data/\n\n",
                      "# Backup configuration\n",
                      "cp -r config/ config_backup/\n",
                      "```\n\n",
                      ])

        return "\n".join(guide)

    def _analyze_source_code(self, source_dir: Path) -> List[CodeEntity]:
        """
        Analisa código fonte e extrai entidades.

        Args:
            source_dir: Diretório fonte

        Returns:
            Lista de entidades de código
        """
        entities = []

        for py_file in source_dir.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        entities.append(
                            self._extract_class_entity(
                                node, py_file))
                    elif isinstance(node, ast.FunctionDef) and not isinstance(
                        node, ast.AsyncFunctionDef
                    ):
                        entities.append(
                            self._extract_function_entity(
                                node, py_file, "function"))
                    elif isinstance(node, ast.AsyncFunctionDef):
                        entities.append(
                            self._extract_function_entity(
                                node, py_file, "async_function"
                            )
                        )

            except Exception as e:
                logger.warning(f"Failed to analyze {py_file}: {e}")

        return entities

    def _extract_class_entity(
            self,
            node: ast.ClassDef,
            file_path: Path) -> CodeEntity:
        """Extrai entidade de classe."""
        docstring = ast.get_docstring(node)
        signature = f"class {node.name}"

        if node.bases:
            base_names = [self._get_node_name(base) for base in node.bases]
            signature += f"({', '.join(base_names)})"

        return CodeEntity(
            name=node.name,
            type="class",
            file_path=file_path,
            line_number=node.lineno,
            docstring=docstring,
            signature=signature,
        )

    def _extract_function_entity(
        self, node: ast.FunctionDef, file_path: Path, func_type: str
    ) -> CodeEntity:
        """Extrai entidade de função."""
        docstring = ast.get_docstring(node)
        signature = f"def {node.name}({self._format_args(node.args)})"

        return CodeEntity(
            name=node.name,
            type=func_type,
            file_path=file_path,
            line_number=node.lineno,
            docstring=docstring,
            signature=signature,
        )

    def _format_args(self, args: ast.arguments) -> str:
        """Formata argumentos de função."""
        arg_list = []

        # Args posicionais
        for arg in args.args:
            arg_list.append(arg.arg)

        # Args com valor padrão
        if args.defaults:
            start_idx = len(args.args) - len(args.defaults)
            for i, default in enumerate(args.defaults):
                arg_name = args.args[start_idx + i].arg
                arg_list[start_idx + i] = (
                    f"{arg_name}={self._get_default_value(default)}"
                )

        # *args
        if args.vararg:
            arg_list.append(f"*{args.vararg.arg}")

        # **kwargs
        if args.kwarg:
            arg_list.append(f"**{args.kwarg.arg}")

        return ", ".join(arg_list)

    def _get_default_value(self, node: ast.AST) -> str:
        """Obtém valor padrão formatado."""
        if isinstance(node, ast.Str):
            return f'"{node.s}"'
        elif isinstance(node, ast.Num):
            return str(node.n)
        elif isinstance(node, ast.NameConstant):
            return str(node.value)
        elif isinstance(node, ast.List):
            return "[]"
        elif isinstance(node, ast.Dict):
            return "{}"
        else:
            return "..."

    def _get_node_name(self, node: ast.AST) -> str:
        """Obtém nome de um nó AST."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_node_name(node.value)}.{node.attr}"
        else:
            return str(node)

    def _get_module_name(self, file_path: Path) -> str:
        """Obtém nome do módulo a partir do caminho."""
        try:
            relative = file_path.relative_to(self.project_root / "src")
            return str(relative).replace(
                "/",
                ".").replace(
                "\\",
                ".").replace(
                ".py",
                "")
        except BaseException:
            return file_path.stem

    def _format_entity_documentation(self, entity: CodeEntity) -> str:
        """Formata documentação de entidade."""
        doc = [f"#### {entity.name}\n"]

        if entity.signature:
            doc.append(f"```python\n{entity.signature}\n```\n")

        if entity.docstring:
            # Formata docstring
            formatted_doc = self._format_docstring(entity.docstring)
            doc.append(f"{formatted_doc}\n")

        doc.append(
            f"**File:** {entity.file_path.name}:{entity.line_number}\n\n")

        return "".join(doc)

    def _format_docstring(self, docstring: str) -> str:
        """Formata docstring para Markdown."""
        if not docstring:
            return ""

        lines = docstring.split("\n")
        formatted_lines = []

        for line in lines:
            line = line.strip()
            if (
                line.startswith("Args:")
                or line.startswith("Returns:")
                or line.startswith("Raises:")
            ):
                formatted_lines.append(f"**{line}**")
            elif line.startswith("    ") or line.startswith("\t"):
                # Indentação para listas
                formatted_lines.append(f"- {line.strip()}")
            else:
                formatted_lines.append(line)

        return "\n".join(formatted_lines)

    def _generate_features_section(self) -> DocumentationSection:
        """Gera seção de features."""
        features = [
            "🤖 Advanced AI Assistant with self-evolution capabilities",
            "🔒 Enterprise-grade security with command validation and path traversal protection",
            "⚡ High-performance architecture with lazy loading and memory management",
            "📊 Comprehensive monitoring and metrics collection",
            "🔄 Auto-healing and predictive maintenance",
            "🧪 Extensive testing suite with performance benchmarks",
            "📚 Automatic documentation generation",
            "🚀 Flexible deployment options (Docker, systemd, standalone)",
        ]

        content = (
            "## Features\n\n"
            + "\n".join(f"- {feature}" for feature in features)
            + "\n\n"
        )
        return DocumentationSection("Features", content)

    def _generate_installation_section(self) -> DocumentationSection:
        """Gera seção de instalação."""
        content = """## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd PROJECT_JARVIS_5.0

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run the system
python main.py
```

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Generate documentation
python -c "from src.utils.documentation_generator import DocumentationGenerator; dg = DocumentationGenerator(); print(dg.generate_readme())"
```
"""
        return DocumentationSection("Installation", content)

    def _generate_usage_section(self) -> DocumentationSection:
        """Gera seção de uso."""
        content = """## Usage

### Basic Operation
```python
from src.core.main import JarvisSystem

# Initialize system
jarvis = JarvisSystem()

# Start the system
await jarvis.start()

# Execute commands
result = await jarvis.execute_command("show system status")

# Stop the system
await jarvis.stop()
```

### Configuration
The system uses hierarchical configuration:
- `config/default.yaml` - Default settings
- `config/user.yaml` - User overrides
- `config/runtime.yaml` - Runtime modifications

### Monitoring
Access the web interface at `http://localhost:8080` for real-time monitoring.
"""
        return DocumentationSection("Usage", content)

    def _generate_architecture_section(self) -> DocumentationSection:
        """Gera seção de arquitetura."""
        content = """## Architecture

JARVIS 5.0 follows a modular, event-driven architecture:

### Core Components
- **SecurityManager**: Handles authentication, authorization, and command validation
- **ConfigManager**: Hierarchical configuration system
- **GlobalEventBus**: Inter-component communication
- **ActionController**: Command execution and workflow management

### Evolution Layer
- **SelfObserver**: System introspection and metrics
- **AutoHealer**: Automatic problem detection and resolution
- **TraceManager**: Distributed tracing and observability
- **AlertManager**: Intelligent alerting system

### Interface Layer
- **BaseHUD**: Abstract interface for all UI components
- **HUDManager**: Interface lifecycle management

### Testing & Quality
- **JarvisTestSuite**: Comprehensive test suite
- **PerformanceTestSuite**: Load testing and benchmarking
- **DocumentationGenerator**: Automatic documentation
"""
        return DocumentationSection("Architecture", content)

    def _generate_api_section(self) -> DocumentationSection:
        """Gera seção de API."""
        content = """## API Reference

For detailed API documentation, see [API Documentation](api/README.md).

### Core Classes
- `JarvisSystem`: Main system class
- `SecurityManager`: Security operations
- `ConfigManager`: Configuration management
- `GlobalEventBus`: Event system

### Evolution Classes
- `SelfObserver`: System monitoring
- `AutoHealer`: Self-healing
- `TraceManager`: Tracing
- `AlertManager`: Alerting
"""
        return DocumentationSection("API Reference", content)

    def _generate_testing_section(self) -> DocumentationSection:
        """Gera seção de testes."""
        content = """## Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run performance tests
python tests/performance_test_suite.py

# Run specific test suite
python -m pytest tests/jarvis_test_suite.py
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Performance Tests**: Load and stress testing
- **System Tests**: End-to-end testing

### Test Results
Test results are saved in `tests/results/` directory.
Performance reports include latency, throughput, and resource usage metrics.
"""
        return DocumentationSection("Testing", content)

    def _generate_deployment_section(self) -> DocumentationSection:
        """Gera seção de deployment."""
        content = """## Deployment

### Docker Deployment
```bash
# Build image
docker build -t jarvis-5.0 .

# Run container
docker run -d -p 8080:8080 --name jarvis jarvis-5.0
```

### Systemd Service
```bash
# Create service file
sudo cp deploy/jarvis.service /etc/systemd/system/

# Enable and start
sudo systemctl enable jarvis
sudo systemctl start jarvis
```

### Configuration
- Production configs: `config/production/`
- Environment variables override config files
- Secrets management through secure config files

See [Deployment Guide](docs/deployment.md) for detailed instructions.
"""
        return DocumentationSection("Deployment", content)

    def _generate_contributing_section(self) -> DocumentationSection:
        """Gera seção de contribuição."""
        content = """## Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Standards
- Follow PEP 8 style guidelines
- Add docstrings to all public functions
- Write comprehensive unit tests
- Update documentation for API changes

### Testing Requirements
- All new code must have unit tests
- Integration tests for new features
- Performance tests for performance-critical code
- Documentation updates for user-facing changes
"""
        return DocumentationSection("Contributing", content)

    def _generate_license_section(self) -> DocumentationSection:
        """Gera seção de licença."""
        content = """## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/your-repo/issues)
- Discussions: [GitHub Discussions](https://github.com/your-repo/discussions)
"""
        return DocumentationSection("License", content)

    def _render_section(self, section: DocumentationSection) -> str:
        """Renderiza seção para Markdown."""
        header = "#" * section.level
        content = f"{header} {section.title}\n\n{section.content}\n"

        for subsection in section.subsections:
            content += self._render_section(subsection)

        return content

    def save_documentation(self, content: str, filename: str):
        """
        Salva documentação em arquivo.

        Args:
            content: Conteúdo da documentação
            filename: Nome do arquivo
        """
        file_path = self.docs_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Documentation saved to {file_path}")


# Função de conveniência
def generate_full_documentation(project_root: Path = None):
    """
    Gera documentação completa do projeto.

    Args:
        project_root: Raiz do projeto
    """
    generator = DocumentationGenerator(project_root)

    # Gera diferentes tipos de documentação
    docs = {
        "README.md": generator.generate_readme(),
        "api.md": generator.generate_api_documentation(),
        "architecture.md": generator.generate_architecture_documentation(),
        "deployment.md": generator.generate_deployment_guide(),
    }

    for filename, content in docs.items():
        generator.save_documentation(content, filename)

    print("Documentation generated successfully!")
    print(f"Files saved in: {generator.docs_dir}")


if __name__ == "__main__":
    # Gera documentação quando executado diretamente
    generate_full_documentation()
