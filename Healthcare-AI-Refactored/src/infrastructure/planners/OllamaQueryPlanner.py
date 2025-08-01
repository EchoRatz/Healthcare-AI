"""Ollama-based query planner for chain-of-thought reasoning."""

import json
import yaml
from typing import Dict, Any, Optional, List

from core.interfaces.QueryPlannerInterface import QueryPlannerInterface
from core.interfaces.LLMInterface import LLMInterface
from shared.logging.LoggerMixin import LoggerMixin


class OllamaQueryPlanner(QueryPlannerInterface, LoggerMixin):
    """Query planner using Ollama for chain-of-thought reasoning."""
    
    def __init__(self, llm_client: LLMInterface):
        super().__init__()
        self.llm_client = llm_client
        self.planning_prompt = self._build_planning_prompt()
    
    def plan(self, query: str) -> Dict[str, Any]:
        """
        Analyze a query and create a structured retrieval plan.
        
        Args:
            query: The user's question
            
        Returns:
            Structured plan specifying what data to fetch from each source
        """
        try:
            self.logger.info(f"Planning retrieval for query: {query[:100]}...")
            
            # Generate plan using Ollama
            plan_response = self.llm_client.generate_response(
                prompt=self.planning_prompt.format(query=query),
                temperature=0.1,  # Low temperature for consistent planning
                max_tokens=1000
            )
            
            if not plan_response:
                self.logger.error("Failed to generate plan")
                return self._get_default_plan()
            
            # Parse the plan response
            plan = self._parse_plan_response(plan_response)
            
            self.logger.info(f"Generated plan with {len(plan.get('mcp', []))} MCP requests, "
                           f"{len(plan.get('pdf', []))} PDF requests, "
                           f"{len(plan.get('text', []))} text requests")
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Failed to create plan: {e}")
            return self._get_default_plan()
    
    def _build_planning_prompt(self) -> str:
        """Build the planning prompt for chain-of-thought reasoning."""
        return """You are a query planner for an AI system that can access multiple data sources:
1. MCP (Model Context Protocol) server - for structured data and APIs
   Available MCP tools:
   
   Patient Management:
   - lookup_patient: Look up patient information by patient ID
   - search_patients: Search patients by name, phone, or email
   - create_patient: Create a new patient record
   - emergency_patient_lookup: Emergency lookup - search by any identifier
   - get_medical_history: Get complete medical history for a patient
   - add_vital_signs: Add vital signs for a patient
   - add_medication: Add medication to patient's record
   - add_allergy: Add allergy to patient's record
   - check_food_allergies: Check if patient has allergies to specific food items
   - check_drug_allergies: Check if patient has allergies to specific medications
   - get_allergy_alternatives: Get alternative foods or medications for allergic patients
   
   Appointment Management:
   - get_appointments: Get patient appointments
   - schedule_appointment: Schedule a new appointment
   - book_appointment_with_availability_check: Book appointment with automatic availability checking
   - book_appointment_with_doctor_recommendation: Book appointment with automatic doctor recommendation
   - find_next_available_appointment: Find the next available appointment slot for a doctor
   - cancel_appointment: Cancel an appointment and free up the doctor's time slot
   
   Doctor & Staff Management:
   - get_doctor_info: Get detailed information about a doctor
   - search_doctors: Search doctors
   - get_doctor_schedule: Get doctor's schedule for a specific date or week
   - check_doctor_availability: Check if doctor is available at specific date and time
   - find_available_doctors: Find available doctors by specialty on a specific date
   - get_staff_info: Get staff member information
   - list_staff_by_department: List all staff members in a department
   
   Department Management:
   - list_all_departments: List all hospital departments
   - get_department_info: Get department information
   - get_department_staff: Get all staff members in a department
   - get_department_services: Get services offered by a department
   
   Room Management:
   - get_room_info: Get detailed room information
   - find_available_rooms: Find available rooms
   - get_room_equipment: Get equipment available in a room
   - update_room_status: Update room status (available, occupied, maintenance, cleaning)
   
   Queue Management:
   - book_queue: Book a queue number for a patient in a specific department
   - check_queue_status: Check the status of a queue number
   - get_department_queue_status: Get current queue status for a department
   
   Lab Management:
   - get_lab_results: Get lab results for a patient
   - add_lab_result: Add lab result for a patient (results should be JSON string)
   
2. PDF files - for documents and manuals
3. Text files - for notes, configurations, and other text data

Analyze the following question and create a structured plan for retrieving relevant information.

Question: {query}

Think step by step:
1. What information is needed to answer this question?
2. Which data sources are most likely to have this information?
3. What specific requests should be made to each source?

Create a plan in YAML format with the following structure:

plan:
  mcp:
    - endpoint: "tool_name"
      params:
        name: "tool_name"
        arguments: {{}}
        query: "original query for context"
  pdf:
    - file: "filename.pdf"
      pages: [1, 2, 3]  # specific pages, or omit for all pages
  text:
    - file: "filename.txt"
      line_range: [10, 50]  # optional line range, or omit for entire file

For MCP requests, use the most appropriate tool name from the available tools list.
Include the original query in the params for context.

Only include sources that are likely to be relevant. If no specific sources are needed, return an empty plan.

Return only the YAML plan, no additional text."""
    
    def _parse_plan_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured plan."""
        try:
            # Extract YAML from response
            yaml_start = response.find('plan:')
            if yaml_start == -1:
                self.logger.warning("No plan found in response")
                return self._get_default_plan()
            
            yaml_content = response[yaml_start:]
            
            # Parse YAML
            plan = yaml.safe_load(yaml_content)
            
            # Validate and clean the plan
            return self._validate_plan(plan)
            
        except Exception as e:
            self.logger.error(f"Failed to parse plan response: {e}")
            return self._get_default_plan()
    
    def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the parsed plan."""
        validated_plan = {
            'mcp': [],
            'pdf': [],
            'text': []
        }
        
        if not isinstance(plan, dict):
            return validated_plan
        
        # Validate MCP requests
        mcp_requests = plan.get('mcp', [])
        if isinstance(mcp_requests, list):
            for req in mcp_requests:
                if isinstance(req, dict) and 'endpoint' in req:
                    params = req.get('params', {})
                    # Ensure params has the required structure
                    if 'name' not in params:
                        params['name'] = req['endpoint']
                    if 'arguments' not in params:
                        params['arguments'] = {}
                    
                    validated_plan['mcp'].append({
                        'endpoint': req['endpoint'],
                        'params': params
                    })
        
        # Validate PDF requests
        pdf_requests = plan.get('pdf', [])
        if isinstance(pdf_requests, list):
            for req in pdf_requests:
                if isinstance(req, dict) and 'file' in req:
                    validated_plan['pdf'].append({
                        'file': req['file'],
                        'pages': req.get('pages', [])
                    })
        
        # Validate text requests
        text_requests = plan.get('text', [])
        if isinstance(text_requests, list):
            for req in text_requests:
                if isinstance(req, dict) and 'file' in req:
                    validated_plan['text'].append({
                        'file': req['file'],
                        'line_range': req.get('line_range', None)
                    })
        
        return validated_plan
    
    def _get_default_plan(self) -> Dict[str, Any]:
        """Get a default empty plan."""
        return {
            'mcp': [],
            'pdf': [],
            'text': []
        }
    
    def is_available(self) -> bool:
        """Check if the planner is available."""
        return self.llm_client.is_available()
    
    def get_planning_info(self) -> Dict[str, Any]:
        """Get information about the planning capabilities."""
        return {
            'type': 'ollama_query_planner',
            'available': self.is_available(),
            'llm_model': getattr(self.llm_client, 'model_name', 'unknown'),
            'supports_sources': ['mcp', 'pdf', 'text']
        }
    
    def get_available_sources(self) -> List[str]:
        """Get list of available data sources."""
        return ['mcp', 'pdf', 'text']
    
    def estimate_plan_complexity(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate the complexity and resource requirements of a plan."""
        try:
            mcp_count = len(plan.get('mcp', []))
            pdf_count = len(plan.get('pdf', []))
            text_count = len(plan.get('text', []))
            
            total_requests = mcp_count + pdf_count + text_count
            
            complexity = 'low'
            if total_requests > 10:
                complexity = 'high'
            elif total_requests > 5:
                complexity = 'medium'
            
            estimated_time = {
                'mcp': mcp_count * 0.5,  # Network calls
                'pdf': pdf_count * 2.0,   # File processing
                'text': text_count * 0.1, # Fast file reads
                'total': mcp_count * 0.5 + pdf_count * 2.0 + text_count * 0.1
            }
            
            return {
                'complexity': complexity,
                'total_requests': total_requests,
                'estimated_time_seconds': estimated_time,
                'source_breakdown': {
                    'mcp': mcp_count,
                    'pdf': pdf_count,
                    'text': text_count
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to estimate plan complexity: {e}")
            return {
                'complexity': 'unknown',
                'total_requests': 0,
                'estimated_time_seconds': {'total': 0},
                'source_breakdown': {'mcp': 0, 'pdf': 0, 'text': 0}
            } 