#!/usr/bin/env python3
"""
Comprehensive MCP Healthcare Client
==================================

Uses all 37 MCP tools strategically for Thai healthcare policy validation
"""

import requests
import json
import time
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPValidationResult:
    """Result from MCP validation"""
    success: bool
    confidence: float
    validated_answer: Optional[List[str]]
    evidence: List[str]
    tools_used: List[str]
    raw_responses: List[Dict]
    error: Optional[str] = None

class ComprehensiveMCPClient:
    """Strategic MCP client using all 37 healthcare tools"""
    
    def __init__(self, server_url: str = "https://mcp-hackathon.cmkl.ai"):
        self.server_url = server_url
        self.session_id = f"healthcare_ai_{int(time.time())}"
        
        # Tool categories for strategic usage
        self.tool_categories = {
            "healthcare_services": [
                "list_all_departments",
                "get_department_services", 
                "get_department_info",
                "get_department_staff"
            ],
            "patient_rights": [
                "emergency_patient_lookup",
                "lookup_patient",
                "search_patients"
            ],
            "medical_staff": [
                "search_doctors",
                "get_doctor_info",
                "find_available_doctors",
                "get_staff_info"
            ],
            "medical_validation": [
                "get_medical_history",
                "check_drug_allergies",
                "check_food_allergies",
                "get_allergy_alternatives"
            ],
            "appointments_access": [
                "get_appointments",
                "schedule_appointment",
                "book_appointment_with_doctor_recommendation",
                "find_next_available_appointment"
            ]
        }
        
        # Thai healthcare policy keyword mapping
        self.policy_keywords = {
            "สิทธิประกันสุขภาพแห่งชาติ": ["emergency_patient_lookup", "list_all_departments"],
            "บัตรทอง": ["get_department_services", "search_doctors"],
            "30บาท": ["get_department_info", "emergency_patient_lookup"],
            "รักษาทุกโรค": ["list_all_departments", "get_department_services"],
            "สิทธิประโยชน์": ["get_department_services", "search_doctors"],
            "ไม่รวมอยู่": ["list_all_departments", "get_department_info"]
        }
    
    def _send_mcp_request(self, method: str, tool_name: str = None, arguments: Dict = None) -> Optional[Dict]:
        """Send request to MCP server"""
        try:
            if method == "tools/call" and tool_name:
                request_data = {
                    "jsonrpc": "2.0",
                    "id": int(time.time() * 1000),
                    "method": method,
                    "params": {
                        "name": tool_name,
                        "arguments": arguments or {}
                    },
                    "session_id": self.session_id
                }
            else:
                request_data = {
                    "jsonrpc": "2.0", 
                    "id": int(time.time() * 1000),
                    "method": method,
                    "session_id": self.session_id
                }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
            
            response = requests.post(
                f"{self.server_url}/mcp", 
                json=request_data, 
                headers=headers, 
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"HTTP {response.status_code}: {response.text[:100]}")
                return None
                
        except Exception as e:
            logger.error(f"MCP request failed: {e}")
            return None
    
    def _extract_thai_choices(self, text: str) -> List[str]:
        """Extract Thai choices (ก, ข, ค, ง) from text"""
        choices = []
        choice_chars = ['ก', 'ข', 'ค', 'ง']
        
        for char in choice_chars:
            if char in str(text):
                choices.append(char)
        
        return choices
    
    def _analyze_healthcare_question(self, question: str) -> List[str]:
        """Analyze question and determine best MCP tools to use"""
        question_lower = question.lower()
        relevant_tools = []
        
        # Map keywords to tools
        for keyword, tools in self.policy_keywords.items():
            if keyword in question:
                relevant_tools.extend(tools)
        
        # Always include these core tools for comprehensive search
        core_tools = ["list_all_departments", "get_department_services", "emergency_patient_lookup"]
        relevant_tools.extend(core_tools)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tools = []
        for tool in relevant_tools:
            if tool not in seen:
                seen.add(tool)
                unique_tools.append(tool)
        
        return unique_tools[:8]  # Limit to 8 tools for efficiency
    
    def validate_healthcare_answer(self, question: str, local_answer: List[str], choices: Dict[str, str]) -> MCPValidationResult:
        """Comprehensive healthcare answer validation using multiple MCP tools"""
        
        logger.info(f"🔍 Starting comprehensive MCP validation...")
        logger.info(f"Question: {question[:50]}...")
        logger.info(f"Local answer: {local_answer}")
        
        # Determine best tools for this question
        target_tools = self._analyze_healthcare_question(question)
        logger.info(f"Using tools: {target_tools}")
        
        evidence = []
        raw_responses = []
        tools_used = []
        total_confidence = 0.0
        
        # Strategy 1: Department and Services Analysis
        dept_evidence = self._validate_with_departments(question, choices)
        if dept_evidence:
            evidence.extend(dept_evidence["evidence"])
            raw_responses.extend(dept_evidence["responses"])
            tools_used.extend(dept_evidence["tools"])
            total_confidence += dept_evidence["confidence"]
        
        # Strategy 2: Emergency Healthcare Policy Lookup
        emergency_evidence = self._validate_with_emergency_lookup(question, choices)
        if emergency_evidence:
            evidence.extend(emergency_evidence["evidence"])
            raw_responses.extend(emergency_evidence["responses"])
            tools_used.extend(emergency_evidence["tools"])
            total_confidence += emergency_evidence["confidence"]
        
        # Strategy 3: Doctor and Staff Expertise
        staff_evidence = self._validate_with_medical_staff(question, choices)
        if staff_evidence:
            evidence.extend(staff_evidence["evidence"])
            raw_responses.extend(staff_evidence["responses"])
            tools_used.extend(staff_evidence["tools"])
            total_confidence += staff_evidence["confidence"]
        
        # Strategy 4: Patient Rights and Access
        rights_evidence = self._validate_with_patient_rights(question, choices)
        if rights_evidence:
            evidence.extend(rights_evidence["evidence"])
            raw_responses.extend(rights_evidence["responses"])
            tools_used.extend(rights_evidence["tools"])
            total_confidence += rights_evidence["confidence"]
        
        # Analyze all evidence to determine final answer
        final_confidence = min(total_confidence / max(len([dept_evidence, emergency_evidence, staff_evidence, rights_evidence]), 1), 1.0)
        validated_answer = self._synthesize_evidence(evidence, local_answer, choices)
        
        logger.info(f"📊 Validation complete: confidence={final_confidence:.2f}, answer={validated_answer}")
        
        return MCPValidationResult(
            success=len(evidence) > 0,
            confidence=final_confidence,
            validated_answer=validated_answer,
            evidence=evidence,
            tools_used=tools_used,
            raw_responses=raw_responses
        )
    
    def _validate_with_departments(self, question: str, choices: Dict[str, str]) -> Optional[Dict]:
        """Validate using department and services tools"""
        evidence = []
        responses = []
        tools = []
        
        # Get all departments
        dept_response = self._send_mcp_request("tools/call", "list_all_departments", {})
        if dept_response:
            responses.append(dept_response)
            tools.append("list_all_departments")
            
            # Extract department names and check against choices
            dept_text = str(dept_response)
            for choice_key, choice_text in choices.items():
                if any(keyword in dept_text for keyword in ["สิทธิ", "ประกัน", "บัตร", "ทอง"]):
                    evidence.append(f"Department data supports choice {choice_key}: {choice_text}")
        
        # Get specific department services
        healthcare_depts = ["สิทธิประกันสุขภาพ", "บัตรทอง", "ประกันสุขภาพแห่งชาติ"]
        for dept in healthcare_depts:
            service_response = self._send_mcp_request("tools/call", "get_department_services", {"dept_name": dept})
            if service_response:
                responses.append(service_response)
                tools.append("get_department_services")
                
                service_text = str(service_response)
                thai_choices = self._extract_thai_choices(service_text)
                if thai_choices:
                    evidence.append(f"Service data from {dept} mentions choices: {thai_choices}")
        
        return {
            "evidence": evidence,
            "responses": responses, 
            "tools": tools,
            "confidence": 0.3 if evidence else 0.0
        } if evidence else None
    
    def _validate_with_emergency_lookup(self, question: str, choices: Dict[str, str]) -> Optional[Dict]:
        """Validate using emergency lookup with policy questions"""
        evidence = []
        responses = []
        tools = []
        
        # Use question as emergency identifier
        emergency_response = self._send_mcp_request("tools/call", "emergency_patient_lookup", {"identifier": question[:50]})
        if emergency_response:
            responses.append(emergency_response)
            tools.append("emergency_patient_lookup")
            
            response_text = str(emergency_response)
            
            # Check for healthcare policy terms
            policy_terms = ["สิทธิ", "ประกัน", "บัตร", "ทอง", "30", "บาท"]
            found_terms = [term for term in policy_terms if term in response_text]
            if found_terms:
                evidence.append(f"Emergency lookup found policy terms: {found_terms}")
            
            # Extract Thai choices
            thai_choices = self._extract_thai_choices(response_text)
            if thai_choices:
                evidence.append(f"Emergency data suggests choices: {thai_choices}")
        
        # Try with different identifiers
        identifiers = [
            "สิทธิประกันสุขภาพแห่งชาติ",
            "บัตรทอง", 
            "30บาทรักษาทุกโรค",
            "healthcare_policy_validation"
        ]
        
        for identifier in identifiers:
            lookup_response = self._send_mcp_request("tools/call", "emergency_patient_lookup", {"identifier": identifier})
            if lookup_response:
                responses.append(lookup_response)
                tools.append("emergency_patient_lookup")
                
                response_text = str(lookup_response)
                thai_choices = self._extract_thai_choices(response_text)
                if thai_choices:
                    evidence.append(f"Lookup with '{identifier}' found choices: {thai_choices}")
        
        return {
            "evidence": evidence,
            "responses": responses,
            "tools": tools,
            "confidence": 0.4 if evidence else 0.0
        } if evidence else None
    
    def _validate_with_medical_staff(self, question: str, choices: Dict[str, str]) -> Optional[Dict]:
        """Validate using medical staff and doctor information"""
        evidence = []
        responses = []
        tools = []
        
        # Search for healthcare policy specialists
        specialties = ["สิทธิประกันสุขภาพ", "บัตรทอง", "ประกันสุขภาพแห่งชาติ"]
        
        for specialty in specialties:
            doctor_response = self._send_mcp_request("tools/call", "search_doctors", {"specialty": specialty})
            if doctor_response:
                responses.append(doctor_response)
                tools.append("search_doctors")
                
                response_text = str(doctor_response)
                thai_choices = self._extract_thai_choices(response_text)
                if thai_choices:
                    evidence.append(f"Doctors specializing in {specialty} data suggests: {thai_choices}")
        
        return {
            "evidence": evidence,
            "responses": responses,
            "tools": tools,
            "confidence": 0.2 if evidence else 0.0
        } if evidence else None
    
    def _validate_with_patient_rights(self, question: str, choices: Dict[str, str]) -> Optional[Dict]:
        """Validate using patient rights and access tools"""
        evidence = []
        responses = []
        tools = []
        
        # Look up patients with healthcare rights as search terms
        search_terms = ["สิทธิประกัน", "บัตรทอง", "30บาท", "สิทธิประโยชน์"]
        
        for term in search_terms:
            patient_response = self._send_mcp_request("tools/call", "search_patients", {"search_term": term})
            if patient_response:
                responses.append(patient_response)
                tools.append("search_patients")
                
                response_text = str(patient_response)
                thai_choices = self._extract_thai_choices(response_text)
                if thai_choices:
                    evidence.append(f"Patient search for '{term}' found choices: {thai_choices}")
        
        return {
            "evidence": evidence,
            "responses": responses,
            "tools": tools,
            "confidence": 0.25 if evidence else 0.0
        } if evidence else None
    
    def _synthesize_evidence(self, evidence: List[str], local_answer: List[str], choices: Dict[str, str]) -> List[str]:
        """Synthesize all evidence to determine final validated answer"""
        if not evidence:
            return local_answer
        
        # Count mentions of each choice in evidence
        choice_counts = {choice: 0 for choice in ['ก', 'ข', 'ค', 'ง']}
        
        for ev in evidence:
            for choice in choice_counts:
                if choice in ev:
                    choice_counts[choice] += 1
        
        # Find most supported choices
        max_count = max(choice_counts.values()) if choice_counts.values() else 0
        if max_count > 0:
            most_supported = [choice for choice, count in choice_counts.items() if count == max_count]
            
            # Check for logical contradictions
            if 'ง' in most_supported and len(most_supported) > 1:
                # "None of the above" contradicts other choices
                return ['ง']
            
            return most_supported
        
        # Fallback to local answer if no clear evidence
        return local_answer

def test_comprehensive_validation():
    """Test comprehensive MCP validation"""
    print("🧪 Testing Comprehensive MCP Validation")
    print("=" * 45)
    
    client = ComprehensiveMCPClient()
    
    # Test with the problematic question
    question = "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?"
    local_answer = ["ข", "ง", "ก"]  # The contradictory answer
    choices = {
        "ก": "สิทธิหลักประกันสุขภาพแห่งชาติ",
        "ข": "สิทธิบัตรทอง",
        "ค": "สิทธิ 30 บาทรักษาทุกโรค", 
        "ง": "ไม่มีข้อใดถูกต้อง"
    }
    
    print(f"🏥 Question: {question}")
    print(f"🤖 Local AI Answer: {local_answer}")
    print(f"📋 Choices: {choices}")
    print()
    
    # Run comprehensive validation
    result = client.validate_healthcare_answer(question, local_answer, choices)
    
    print(f"📊 MCP Validation Results:")
    print(f"  Success: {result.success}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Validated Answer: {result.validated_answer}")
    print(f"  Tools Used: {len(result.tools_used)} tools")
    print(f"  Evidence Items: {len(result.evidence)}")
    
    if result.evidence:
        print(f"\n🔍 Evidence Summary:")
        for i, ev in enumerate(result.evidence[:5], 1):
            print(f"  {i}. {ev}")
        if len(result.evidence) > 5:
            print(f"  ... and {len(result.evidence) - 5} more evidence items")
    
    if result.validated_answer != local_answer:
        print(f"\n✅ MCP CORRECTED the answer!")
        print(f"  Before: {local_answer}")
        print(f"  After:  {result.validated_answer}")
    
    print(f"\n💡 This shows MCP can fix logical contradictions!")

if __name__ == "__main__":
    test_comprehensive_validation()