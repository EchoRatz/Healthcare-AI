"""Factory for creating the enhanced chain-of-thought system."""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from core.interfaces.LLMInterface import LLMInterface
from core.interfaces.QueryPlannerInterface import QueryPlannerInterface
from core.interfaces.DataConnectorInterface import DataConnectorInterface
from core.use_cases.ChainOfThoughtEngine import ChainOfThoughtEngine

from infrastructure.llm.OllamaClient import OllamaClient
from infrastructure.planners.OllamaQueryPlanner import OllamaQueryPlanner
from infrastructure.connectors.MCPConnector import MCPConnector
from infrastructure.connectors.PDFConnector import PDFConnector
from infrastructure.connectors.TextConnector import TextConnector

from shared.logging.LoggerMixin import LoggerMixin


class EnhancedSystemFactory(LoggerMixin):
    """Factory for creating the enhanced chain-of-thought system."""
    
    def __init__(self, config_path: str = "config/enhanced_system.json"):
        super().__init__()
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            if not self.config_path.exists():
                self.logger.warning(f"Config file not found: {self.config_path}")
                return self._get_default_config()
            
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            self.logger.info(f"Loaded configuration from {self.config_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "llm": {
                "provider": "ollama",
                "model_name": "llama2",
                "base_url": "http://localhost:11434",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "connectors": {
                "mcp": {"enabled": False},
                "pdf": {"enabled": True, "base_path": "data/documents"},
                "text": {"enabled": True, "base_path": "data/documents"}
            }
        }
    
    def create_llm_client(self) -> LLMInterface:
        """Create the LLM client."""
        try:
            llm_config = self.config.get('llm', {})
            
            client = OllamaClient(
                base_url=llm_config.get('base_url', 'http://localhost:11434'),
                model_name=llm_config.get('model_name', 'llama2')
            )
            
            # Set parameters
            parameters = {
                'temperature': llm_config.get('temperature', 0.7),
                'max_tokens': llm_config.get('max_tokens', 1000)
            }
            client.set_parameters(parameters)
            
            self.logger.info(f"Created LLM client with model: {llm_config.get('model_name')}")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to create LLM client: {e}")
            raise
    
    def create_query_planner(self, llm_client: LLMInterface) -> QueryPlannerInterface:
        """Create the query planner."""
        try:
            planner_config = self.config.get('query_planner', {})
            
            planner = OllamaQueryPlanner(llm_client)
            
            self.logger.info("Created query planner")
            return planner
            
        except Exception as e:
            self.logger.error(f"Failed to create query planner: {e}")
            raise
    
    def create_mcp_connector(self) -> Optional[DataConnectorInterface]:
        """Create the MCP connector if enabled."""
        try:
            mcp_config = self.config.get('connectors', {}).get('mcp', {})
            
            if not mcp_config.get('enabled', False):
                self.logger.info("MCP connector disabled")
                return None
            
            connector = MCPConnector(
                server_url=mcp_config.get('server_url', 'http://localhost:3000'),
                auth_token=mcp_config.get('auth_token')
            )
            
            self.logger.info(f"Created MCP connector for {mcp_config.get('server_url')}")
            return connector
            
        except Exception as e:
            self.logger.error(f"Failed to create MCP connector: {e}")
            return None
    
    def create_pdf_connector(self) -> Optional[DataConnectorInterface]:
        """Create the PDF connector if enabled."""
        try:
            pdf_config = self.config.get('connectors', {}).get('pdf', {})
            
            if not pdf_config.get('enabled', True):
                self.logger.info("PDF connector disabled")
                return None
            
            connector = PDFConnector(
                base_path=pdf_config.get('base_path', 'data/documents')
            )
            
            self.logger.info(f"Created PDF connector with base path: {pdf_config.get('base_path')}")
            return connector
            
        except Exception as e:
            self.logger.error(f"Failed to create PDF connector: {e}")
            return None
    
    def create_text_connector(self) -> Optional[DataConnectorInterface]:
        """Create the text connector if enabled."""
        try:
            text_config = self.config.get('connectors', {}).get('text', {})
            
            if not text_config.get('enabled', True):
                self.logger.info("Text connector disabled")
                return None
            
            connector = TextConnector(
                base_path=text_config.get('base_path', 'data/documents')
            )
            
            self.logger.info(f"Created text connector with base path: {text_config.get('base_path')}")
            return connector
            
        except Exception as e:
            self.logger.error(f"Failed to create text connector: {e}")
            return None
    
    def create_chain_of_thought_engine(self) -> ChainOfThoughtEngine:
        """Create the complete chain-of-thought engine."""
        try:
            # Create LLM client
            llm_client = self.create_llm_client()
            
            # Create query planner
            query_planner = self.create_query_planner(llm_client)
            
            # Create connectors
            mcp_connector = self.create_mcp_connector()
            pdf_connector = self.create_pdf_connector()
            text_connector = self.create_text_connector()
            
            # Create the engine
            engine = ChainOfThoughtEngine(
                query_planner=query_planner,
                llm_client=llm_client,
                mcp_connector=mcp_connector,
                pdf_connector=pdf_connector,
                text_connector=text_connector
            )
            
            self.logger.info("Created enhanced chain-of-thought engine")
            return engine
            
        except Exception as e:
            self.logger.error(f"Failed to create chain-of-thought engine: {e}")
            raise
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the status of all system components."""
        try:
            status = {
                'config_loaded': self.config is not None,
                'config_path': str(self.config_path),
                'components': {}
            }
            
            # Test LLM
            try:
                llm_client = self.create_llm_client()
                status['components']['llm'] = {
                    'available': llm_client.is_available(),
                    'model_info': llm_client.get_model_info()
                }
            except Exception as e:
                status['components']['llm'] = {'available': False, 'error': str(e)}
            
            # Test connectors
            for connector_name, creator_func in [
                ('mcp', self.create_mcp_connector),
                ('pdf', self.create_pdf_connector),
                ('text', self.create_text_connector)
            ]:
                try:
                    connector = creator_func()
                    if connector:
                        status['components'][connector_name] = {
                            'available': connector.is_available(),
                            'info': connector.get_connector_info()
                        }
                    else:
                        status['components'][connector_name] = {'available': False, 'reason': 'disabled'}
                except Exception as e:
                    status['components'][connector_name] = {'available': False, 'error': str(e)}
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {'error': str(e)}
    
    def validate_system(self) -> Dict[str, Any]:
        """Validate that the system can be created and is ready to use."""
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'components': {}
            }
            
            # Test system creation
            try:
                engine = self.create_chain_of_thought_engine()
                validation_result['components']['engine'] = {'status': 'created'}
            except Exception as e:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Failed to create engine: {e}")
                validation_result['components']['engine'] = {'status': 'failed', 'error': str(e)}
            
            # Test individual components
            for component_name, creator_func in [
                ('llm', self.create_llm_client),
                ('query_planner', lambda: self.create_query_planner(self.create_llm_client())),
                ('mcp_connector', self.create_mcp_connector),
                ('pdf_connector', self.create_pdf_connector),
                ('text_connector', self.create_text_connector)
            ]:
                try:
                    component = creator_func()
                    if component:
                        validation_result['components'][component_name] = {'status': 'available'}
                    else:
                        validation_result['components'][component_name] = {'status': 'disabled'}
                        validation_result['warnings'].append(f"{component_name} is disabled")
                except Exception as e:
                    validation_result['components'][component_name] = {'status': 'error', 'error': str(e)}
                    if component_name in ['llm', 'query_planner']:
                        validation_result['valid'] = False
                        validation_result['errors'].append(f"{component_name} error: {e}")
                    else:
                        validation_result['warnings'].append(f"{component_name} error: {e}")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Failed to validate system: {e}")
            return {
                'valid': False,
                'errors': [f"Validation failed: {e}"],
                'warnings': [],
                'components': {}
            } 