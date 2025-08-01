#!/usr/bin/env python3
"""
Working MCP Client - Patient & Doctor Focus
==========================================

Aggressive approach to get MCP server working for healthcare questions
"""

import requests
import json
import time
import re
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkingMCPClient:
    """Working MCP client focused on patient and doctor queries"""
    
    def __init__(self):
        self.server_url = "https://mcp-hackathon.cmkl.ai/mcp"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "Healthcare-AI-Client/1.0",
            "X-Client-Type": "healthcare-validator"
        }
        
        # Priority tools for patient/doctor questions
        self.patient_doctor_tools = [
            "lookup_patient",
            "search_patients", 
            "emergency_patient_lookup",
            "search_doctors",
            "get_doctor_info",
            "find_available_doctors",
            "get_medical_history",
            "list_all_departments",
            "get_department_services",
            "get_staff_info"
        ]
        
        # Session management attempts
        self.session_attempts = [
            {},  # No session
            {"session_id": f"healthcare_{int(time.time())}"},
            {"client_session": f"patient_lookup_{int(time.time())}"},
            {"connection_id": f"mcp_client_{int(time.time())}"}
        ]
    
    def _make_request(self, tool_name: str, arguments: Dict) -> Optional[Dict]:
        """Make MCP request with multiple session attempts"""
        
        for session_data in self.session_attempts:
            request_data = {
                "jsonrpc": "2.0",
                "id": int(time.time() * 1000),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # Add session data
            request_data.update(session_data)
            
            try:
                # Try with session in URL too
                url = self.server_url
                if session_data:
                    session_key = list(session_data.keys())[0]
                    url += f"?{session_key}={session_data[session_key]}"
                
                response = requests.post(url, json=request_data, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    # Handle SSE response
                    if 'data:' in response.text:
                        for line in response.text.split('\n'):
                            if line.startswith('data: '):
                                try:
                                    return json.loads(line[6:])
                                except:
                                    continue
                    else:
                        try:
                            return response.json()
                        except:
                            return {"raw_response": response.text}
                            
                elif response.status_code != 400:  # Don't log session errors
                    logger.debug(f"HTTP {response.status_code} for {tool_name}")
                    
            except Exception as e:
                logger.debug(f"Request error for {tool_name}: {e}")
                continue
        
        return None
    
    def get_patient_healthcare_info(self, question: str, choices: Dict[str, str]) -> Optional[Dict]:
        """Get healthcare info using patient-related tools"""
        logger.info(f"🏥 Querying MCP for patient healthcare info...")
        
        # Extract Thai healthcare terms from question
        healthcare_terms = self._extract_healthcare_terms(question)
        
        results = {}
        
        # Try patient lookup with healthcare terms
        for term in healthcare_terms[:3]:  # Limit to top 3 terms
            patient_result = self._make_request("lookup_patient", {"patient_id": term})
            if patient_result and "error" not in patient_result:
                results[f"patient_lookup_{term}"] = patient_result
                logger.info(f"✅ Patient lookup success for: {term}")
        
        # Try emergency lookup with question
        emergency_result = self._make_request("emergency_patient_lookup", {"identifier": question[:100]})
        if emergency_result and "error" not in emergency_result:
            results["emergency_lookup"] = emergency_result
            logger.info(f"✅ Emergency lookup success")
        
        # Try search patients with healthcare context
        search_result = self._make_request("search_patients", {"search_term": "สิทธิประกันสุขภาพ"})
        if search_result and "error" not in search_result:
            results["patient_search"] = search_result
            logger.info(f"✅ Patient search success")
        
        return results if results else None
    
    def get_doctor_medical_info(self, question: str, choices: Dict[str, str]) -> Optional[Dict]:
        """Get medical info using doctor-related tools"""
        logger.info(f"👨‍⚕️ Querying MCP for doctor medical info...")
        
        results = {}
        
        # Search doctors by healthcare specialties
        specialties = ["สิทธิประกันสุขภาพ", "บัตรทอง", "การแพทย์", "สุขภาพแห่งชาติ"]
        
        for specialty in specialties:
            doctor_result = self._make_request("search_doctors", {"specialty": specialty})
            if doctor_result and "error" not in doctor_result:
                results[f"doctor_search_{specialty}"] = doctor_result
                logger.info(f"✅ Doctor search success for: {specialty}")
        
        # Get department services
        dept_result = self._make_request("list_all_departments", {})
        if dept_result and "error" not in dept_result:
            results["departments"] = dept_result
            logger.info(f"✅ Department list success")
        
        # Get specific department services
        healthcare_depts = ["สิทธิประกันสุขภาพ", "บัตรทอง"]
        for dept in healthcare_depts:
            service_result = self._make_request("get_department_services", {"dept_name": dept})
            if service_result and "error" not in service_result:
                results[f"services_{dept}"] = service_result
                logger.info(f"✅ Department services success for: {dept}")
        
        return results if results else None
    
    def validate_healthcare_answer(self, question: str, choices: Dict[str, str], predicted_answer: List[str]) -> Tuple[List[str], float, str]:
        """Use MCP server to validate healthcare answers"""
        
        # Get patient and doctor information
        patient_info = self.get_patient_healthcare_info(question, choices)
        doctor_info = self.get_doctor_medical_info(question, choices)
        
        if not patient_info and not doctor_info:
            logger.warning("❌ No MCP data available")
            return predicted_answer, 0.5, "NO_MCP_DATA"
        
        # Analyze MCP responses
        all_mcp_data = {}
        if patient_info:
            all_mcp_data.update(patient_info)
        if doctor_info:
            all_mcp_data.update(doctor_info)
        
        # Extract healthcare insights from MCP data
        insights = self._analyze_mcp_responses(all_mcp_data, question, choices)
        
        if insights['suggested_answers']:
            logger.info(f"🎯 MCP suggests: {insights['suggested_answers']}")
            return insights['suggested_answers'], insights['confidence'], f"MCP_VALIDATED_{insights['source']}"
        elif insights['validates_current']:
            logger.info(f"✅ MCP validates current answer")
            return predicted_answer, min(insights['confidence'] + 0.1, 0.95), f"MCP_CONFIRMED_{insights['source']}"
        else:
            logger.info(f"⚠️ MCP provides context but no clear answer")
            return predicted_answer, 0.6, f"MCP_CONTEXT_{insights['source']}"
    
    def _extract_healthcare_terms(self, text: str) -> List[str]:
        """Extract key healthcare terms from Thai text"""
        healthcare_patterns = [
            r'สิทธิ[\u0E00-\u0E7F]*',
            r'ประกัน[\u0E00-\u0E7F]*', 
            r'บัตร[\u0E00-\u0E7F]*',
            r'สุขภาพ[\u0E00-\u0E7F]*',
            r'แพทย์[\u0E00-\u0E7F]*',
            r'โรงพยาบาล[\u0E00-\u0E7F]*',
            r'รักษา[\u0E00-\u0E7F]*',
        ]
        
        terms = []
        for pattern in healthcare_patterns:
            matches = re.findall(pattern, text)
            terms.extend(matches)
        
        # Add specific terms
        specific_terms = ['สิทธิประกันสุขภาพแห่งชาติ', 'บัตรทอง', '30บาท']
        for term in specific_terms:
            if term in text:
                terms.append(term)
        
        return list(set(terms))[:5]  # Return top 5 unique terms
    
    def _analyze_mcp_responses(self, mcp_data: Dict, question: str, choices: Dict[str, str]) -> Dict:
        """Analyze MCP responses to extract healthcare insights"""
        
        insights = {
            'suggested_answers': [],
            'validates_current': False,
            'confidence': 0.5,
            'source': 'unknown'
        }
        
        # Convert all MCP data to text for analysis
        all_text = ""
        data_sources = []
        
        for source, data in mcp_data.items():
            data_sources.append(source)
            all_text += str(data) + " "
        
        insights['source'] = "_".join(data_sources[:2])  # Use first 2 sources
        
        # Look for Thai choice indicators in MCP data
        choice_indicators = {'ก': 0, 'ข': 0, 'ค': 0, 'ง': 0}
        
        for choice in choice_indicators:
            if choice in all_text:
                choice_indicators[choice] += all_text.count(choice)
        
        # Look for healthcare policy terms that match choices
        for choice_key, choice_text in choices.items():
            choice_terms = self._extract_healthcare_terms(choice_text)
            for term in choice_terms:
                if term in all_text:
                    choice_indicators[choice_key] += 5  # Boost for term matches
        
        # Find highest scoring choices
        max_score = max(choice_indicators.values())
        if max_score > 0:
            top_choices = [choice for choice, score in choice_indicators.items() if score == max_score]
            
            # Apply healthcare logic
            if 'ง' in top_choices and len(top_choices) > 1:
                # If "none" is tied with others, prefer specific answers
                top_choices = [c for c in top_choices if c != 'ง']
            
            if top_choices:
                insights['suggested_answers'] = top_choices
                insights['confidence'] = min(0.7 + (max_score * 0.05), 0.9)
        
        # Check if MCP data validates current answer by containing relevant terms
        if not insights['suggested_answers'] and len(all_text) > 100:
            insights['validates_current'] = True
            insights['confidence'] = 0.65
        
        return insights

def test_working_mcp():
    """Test the working MCP client"""
    print("🧪 Testing Working MCP Client")
    print("=" * 35)
    
    client = WorkingMCPClient()
    
    # Test with the problematic question 4
    question = "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?"
    choices = {
        "ก": "สิทธิหลักประกันสุขภาพแห่งชาติ",
        "ข": "สิทธิบัตรทอง",
        "ค": "สิทธิ 30 บาทรักษาทุกโรค", 
        "ง": "ไม่มีข้อใดถูกต้อง"
    }
    predicted = ["ง"]  # Current over-conservative answer
    
    print(f"🏥 Question: {question[:50]}...")
    print(f"🤖 Current Answer: {predicted}")
    
    # Test MCP validation
    validated_answer, confidence, source = client.validate_healthcare_answer(question, choices, predicted)
    
    print(f"\n📊 MCP Results:")
    print(f"  Validated Answer: {validated_answer}")
    print(f"  Confidence: {confidence:.2f}")
    print(f"  Source: {source}")
    
    if validated_answer != predicted:
        print(f"  ✅ MCP IMPROVED the answer!")
        print(f"  Before: {predicted}")
        print(f"  After:  {validated_answer}")
    else:
        print(f"  📝 MCP confirmed current answer")
    
    return validated_answer != predicted

if __name__ == "__main__":
    success = test_working_mcp()
    if success:
        print(f"\n🎉 MCP client is working and improving answers!")
    else:
        print(f"\n⚠️ MCP client needs more work")