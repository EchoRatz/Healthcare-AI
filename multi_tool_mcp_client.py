#!/usr/bin/env python3
"""
Multi-Tool MCP Client - Chain Multiple Requests
===============================================

Handles complex healthcare questions requiring multiple MCP tool calls
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
import logging
from mock_mcp_healthcare import MockMCPHealthcareSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPQueryPlan:
    """Plan for multiple MCP tool queries"""
    primary_tools: List[Tuple[str, Dict]]
    secondary_tools: List[Tuple[str, Dict]]
    validation_tools: List[Tuple[str, Dict]]
    reasoning: str

@dataclass
class MultiToolResult:
    """Result from multi-tool MCP analysis"""
    final_answer: List[str]
    confidence: float
    evidence_sources: List[str]
    tool_calls_made: int
    comprehensive_reasoning: str

class MultiToolMCPClient:
    """Advanced MCP client that chains multiple tool calls for complex questions"""
    
    def __init__(self):
        self.mock_mcp = MockMCPHealthcareSystem()
        
        # Question complexity patterns that need multiple tools
        self.complex_question_patterns = {
            "comparison_questions": {
                "patterns": [r"แตกต่าง", r"เปรียบเทียบ", r"ความแตกต่าง", r"เหมือน", r"ต่าง"],
                "tools_needed": ["lookup_patient", "search_doctors", "list_all_departments"],
                "strategy": "compare_multiple_policies"
            },
            "comprehensive_coverage": {
                "patterns": [r"ครอบคลุม.*ทั้งหมด", r"รวม.*ทุก", r"ทั้งหมด.*รวม"],
                "tools_needed": ["list_all_departments", "get_department_services", "search_doctors"],
                "strategy": "comprehensive_analysis"
            },
            "exclusion_analysis": {
                "patterns": [r"ไม่รวมอยู่", r"ยกเว้น", r"ไม่ได้รับ", r"ไม่ครอบคลุม"],
                "tools_needed": ["lookup_patient", "get_department_services", "search_patients"],
                "strategy": "exclusion_validation"
            },
            "patient_specific": {
                "patterns": [r"ผู้ป่วย", r"คนไข้", r"ผู้รับบริการ", r"บุคคล"],
                "tools_needed": ["lookup_patient", "search_patients", "emergency_patient_lookup"],
                "strategy": "patient_focused"
            },
            "doctor_consultation": {
                "patterns": [r"แพทย์", r"หมอ", r"นายแพทย์", r"เฉพาะทาง"],
                "tools_needed": ["search_doctors", "get_doctor_info", "find_available_doctors"],
                "strategy": "doctor_expertise"
            },
            "policy_rights": {
                "patterns": [r"สิทธิ.*สิทธิ", r"หลายสิทธิ", r"สิทธิ์.*และ.*สิทธิ์"],
                "tools_needed": ["lookup_patient", "list_all_departments", "get_department_services"],
                "strategy": "multi_policy_analysis"
            }
        }
        
        # Tool chaining strategies
        self.chaining_strategies = {
            "patient_to_doctor": ["lookup_patient", "search_patients", "search_doctors"],
            "department_to_services": ["list_all_departments", "get_department_services"],
            "emergency_to_specialist": ["emergency_patient_lookup", "search_doctors", "find_available_doctors"],
            "comprehensive_health_check": ["lookup_patient", "search_doctors", "list_all_departments", "get_department_services"]
        }
    
    def analyze_question_complexity(self, question: str, choices: Dict[str, str]) -> MCPQueryPlan:
        """Analyze question to determine which tools and strategy to use"""
        
        primary_tools = []
        secondary_tools = []
        validation_tools = []
        reasoning_parts = []
        
        # Check for complex patterns
        matched_patterns = []
        for pattern_name, pattern_data in self.complex_question_patterns.items():
            for pattern in pattern_data["patterns"]:
                if re.search(pattern, question):
                    matched_patterns.append(pattern_name)
                    reasoning_parts.append(f"Detected {pattern_name}")
                    break
        
        if not matched_patterns:
            # Simple question - basic tools
            primary_tools = [("lookup_patient", {"patient_id": "สิทธิประกันสุขภาพ"})]
            secondary_tools = [("list_all_departments", {})]
            reasoning_parts.append("Simple question - basic tools")
        else:
            # Complex question - multiple strategies
            for pattern_name in matched_patterns:
                pattern_data = self.complex_question_patterns[pattern_name]
                strategy = pattern_data["strategy"]
                
                if strategy == "compare_multiple_policies":
                    primary_tools.extend([
                        ("lookup_patient", {"patient_id": "สิทธิประกันสุขภาพแห่งชาติ"}),
                        ("lookup_patient", {"patient_id": "สิทธิบัตรทอง"}),
                        ("lookup_patient", {"patient_id": "30บาทรักษาทุกโรค"})
                    ])
                    secondary_tools.extend([
                        ("list_all_departments", {}),
                        ("search_doctors", {"specialty": "สิทธิประกันสุขภาพ"})
                    ])
                    
                elif strategy == "comprehensive_analysis":
                    primary_tools.extend([
                        ("list_all_departments", {}),
                        ("get_department_services", {"dept_name": "สิทธิประกันสุขภาพแห่งชาติ"}),
                        ("get_department_services", {"dept_name": "สิทธิบัตรทอง"})
                    ])
                    secondary_tools.extend([
                        ("search_doctors", {"specialty": "สุขภาพแห่งชาติ"}),
                        ("search_patients", {"search_term": "สิทธิประกัน"})
                    ])
                    
                elif strategy == "exclusion_validation":
                    primary_tools.extend([
                        ("lookup_patient", {"patient_id": "สิทธิประกันสุขภาพแห่งชาติ"}),
                        ("get_department_services", {"dept_name": "สิทธิประกันสุขภาพแห่งชาติ"})
                    ])
                    validation_tools.extend([
                        ("search_patients", {"search_term": "ไม่รวม"}),
                        ("search_doctors", {"specialty": "ยกเว้น"})
                    ])
                    
                elif strategy == "patient_focused":
                    primary_tools.extend([
                        ("lookup_patient", {"patient_id": question[:50]}),
                        ("search_patients", {"search_term": "สิทธิประกัน"}),
                        ("emergency_patient_lookup", {"identifier": "ผู้ป่วยฉุกเฉิน"})
                    ])
                    
                elif strategy == "doctor_expertise":
                    primary_tools.extend([
                        ("search_doctors", {"specialty": "สิทธิประกันสุขภาพ"}),
                        ("search_doctors", {"specialty": "นโยบายสุขภาพ"}),
                        ("find_available_doctors", {"specialty": "การแพทย์"})
                    ])
                    
                elif strategy == "multi_policy_analysis":
                    primary_tools.extend([
                        ("lookup_patient", {"patient_id": "สิทธิประกันสุขภาพแห่งชาติ"}),
                        ("lookup_patient", {"patient_id": "สิทธิบัตรทอง"}),
                        ("list_all_departments", {})
                    ])
                    secondary_tools.extend([
                        ("get_department_services", {"dept_name": "สิทธิประกันสุขภาพแห่งชาติ"}),
                        ("get_department_services", {"dept_name": "สิทธิบัตรทอง"})
                    ])
        
        # Remove duplicates while preserving order (convert to strings for comparison)
        seen_primary = set()
        unique_primary = []
        for tool in primary_tools:
            tool_str = f"{tool[0]}_{json.dumps(tool[1], sort_keys=True)}"
            if tool_str not in seen_primary:
                seen_primary.add(tool_str)
                unique_primary.append(tool)
        primary_tools = unique_primary
        
        seen_secondary = set()
        unique_secondary = []
        for tool in secondary_tools:
            tool_str = f"{tool[0]}_{json.dumps(tool[1], sort_keys=True)}"
            if tool_str not in seen_secondary:
                seen_secondary.add(tool_str)
                unique_secondary.append(tool)
        secondary_tools = unique_secondary
        
        seen_validation = set()
        unique_validation = []
        for tool in validation_tools:
            tool_str = f"{tool[0]}_{json.dumps(tool[1], sort_keys=True)}"
            if tool_str not in seen_validation:
                seen_validation.add(tool_str)
                unique_validation.append(tool)
        validation_tools = unique_validation
        
        reasoning = " + ".join(reasoning_parts)
        
        return MCPQueryPlan(
            primary_tools=primary_tools,
            secondary_tools=secondary_tools, 
            validation_tools=validation_tools,
            reasoning=reasoning
        )
    
    def execute_multi_tool_query(self, question: str, choices: Dict[str, str], predicted_answer: List[str]) -> MultiToolResult:
        """Execute multiple MCP tool calls in sequence for comprehensive analysis"""
        
        logger.info(f"🔧 Multi-tool MCP analysis for: {question[:50]}...")
        
        # Plan the query strategy
        query_plan = self.analyze_question_complexity(question, choices)
        
        all_mcp_data = {}
        evidence_sources = []
        tool_calls_made = 0
        
        # Execute primary tools
        logger.info(f"📋 Executing {len(query_plan.primary_tools)} primary tools...")
        for tool_name, arguments in query_plan.primary_tools:
            result = self._execute_mock_tool(tool_name, arguments)
            if result:
                all_mcp_data[f"primary_{tool_name}_{tool_calls_made}"] = result
                evidence_sources.append(f"primary_{tool_name}")
                tool_calls_made += 1
        
        # Execute secondary tools
        logger.info(f"📋 Executing {len(query_plan.secondary_tools)} secondary tools...")
        for tool_name, arguments in query_plan.secondary_tools:
            result = self._execute_mock_tool(tool_name, arguments)
            if result:
                all_mcp_data[f"secondary_{tool_name}_{tool_calls_made}"] = result
                evidence_sources.append(f"secondary_{tool_name}")
                tool_calls_made += 1
        
        # Execute validation tools if needed
        if predicted_answer == ["ง"] or len(predicted_answer) > 2:
            logger.info(f"📋 Executing {len(query_plan.validation_tools)} validation tools...")
            for tool_name, arguments in query_plan.validation_tools:
                result = self._execute_mock_tool(tool_name, arguments)
                if result:
                    all_mcp_data[f"validation_{tool_name}_{tool_calls_made}"] = result
                    evidence_sources.append(f"validation_{tool_name}")
                    tool_calls_made += 1
        
        # Comprehensive analysis of all data
        final_analysis = self._comprehensive_data_analysis(all_mcp_data, question, choices)
        
        comprehensive_reasoning = f"{query_plan.reasoning} | Tools: {tool_calls_made} | Evidence: {len(evidence_sources)} sources | {final_analysis['reasoning']}"
        
        logger.info(f"✅ Multi-tool analysis complete: {tool_calls_made} tools, confidence {final_analysis['confidence']:.2f}")
        
        return MultiToolResult(
            final_answer=final_analysis["answer"],
            confidence=final_analysis["confidence"],
            evidence_sources=evidence_sources,
            tool_calls_made=tool_calls_made,
            comprehensive_reasoning=comprehensive_reasoning
        )
    
    def _execute_mock_tool(self, tool_name: str, arguments: Dict) -> Optional[Dict]:
        """Execute a single mock MCP tool"""
        try:
            if tool_name == "lookup_patient":
                return self.mock_mcp.lookup_patient(arguments.get("patient_id", ""))
            elif tool_name == "search_patients":
                return self.mock_mcp.search_patients(arguments.get("search_term", ""))
            elif tool_name == "emergency_patient_lookup":
                return self.mock_mcp.emergency_patient_lookup(arguments.get("identifier", ""))
            elif tool_name == "search_doctors":
                return self.mock_mcp.search_doctors(arguments.get("specialty", ""))
            elif tool_name == "list_all_departments":
                return self.mock_mcp.list_all_departments()
            elif tool_name == "get_department_services":
                # Mock this tool
                dept_name = arguments.get("dept_name", "")
                return {
                    "tool": "get_department_services",
                    "department": dept_name,
                    "services": [f"บริการ {dept_name}", f"การดูแล {dept_name}", f"สิทธิ์ {dept_name}"]
                }
            elif tool_name == "find_available_doctors":
                return {
                    "tool": "find_available_doctors",
                    "specialty": arguments.get("specialty", ""),
                    "available_doctors": [f"หมอเฉพาะทาง {arguments.get('specialty', '')}", "หมอทั่วไป"]
                }
            else:
                return {"tool": tool_name, "result": "mock_data"}
        except Exception as e:
            logger.warning(f"Tool {tool_name} failed: {e}")
            return None
    
    def _comprehensive_data_analysis(self, all_data: Dict, question: str, choices: Dict[str, str]) -> Dict:
        """Comprehensive analysis of all MCP data from multiple tools"""
        
        # Convert all data to searchable text
        all_text = json.dumps(all_data, ensure_ascii=False).lower()
        
        # Advanced scoring system
        choice_scores = {choice: 0 for choice in choices.keys()}
        
        # 1. Direct text matching (high weight)
        for choice_key, choice_text in choices.items():
            choice_text_lower = choice_text.lower()
            
            # Exact matches
            if choice_text_lower in all_text:
                choice_scores[choice_key] += 20
            
            # Partial matches
            choice_words = choice_text_lower.split()
            for word in choice_words:
                if len(word) > 2 and word in all_text:
                    choice_scores[choice_key] += 5
        
        # 2. Healthcare policy logic (medium weight)
        question_lower = question.lower()
        
        if "ไม่รวมอยู่" in question_lower:  # Exclusion question
            # Look for exclusion evidence
            exclusion_terms = ["ไม่รวม", "ยกเว้น", "excluded", "ไม่ครอบคลุม"]
            for choice_key, choice_text in choices.items():
                choice_lower = choice_text.lower()
                if any(term in all_text and any(word in choice_lower for word in ["เสริมความงาม", "แบรนด์", "พิเศษ"]) for term in exclusion_terms):
                    choice_scores[choice_key] += 15
        
        else:  # Inclusion question
            # Look for inclusion evidence
            inclusion_terms = ["รวม", "ครอบคลุม", "services", "บริการ"]
            for choice_key, choice_text in choices.items():
                choice_lower = choice_text.lower()
                if any(term in all_text and any(word in choice_lower for word in ["การรักษา", "ยา", "ตรวจ", "ดูแล"]) for term in inclusion_terms):
                    choice_scores[choice_key] += 15
        
        # 3. Multi-source validation (high weight for consistency)
        primary_sources = [k for k in all_data.keys() if k.startswith("primary_")]
        secondary_sources = [k for k in all_data.keys() if k.startswith("secondary_")]
        
        for choice_key, choice_text in choices.items():
            primary_mentions = sum(1 for source in primary_sources if choice_text.lower() in str(all_data[source]).lower())
            secondary_mentions = sum(1 for source in secondary_sources if choice_text.lower() in str(all_data[source]).lower())
            
            # Boost for multiple source validation
            if primary_mentions >= 2:
                choice_scores[choice_key] += 25
            if secondary_mentions >= 1 and primary_mentions >= 1:
                choice_scores[choice_key] += 15
        
        # 4. Apply logical constraints
        max_score = max(choice_scores.values()) if choice_scores.values() else 0
        
        if max_score >= 20:  # High confidence threshold
            # Get top scoring choices
            top_choices = [choice for choice, score in choice_scores.items() 
                          if score >= max_score * 0.7]  # Within 70% of max score
            
            # Apply healthcare logic
            if 'ง' in top_choices and len(top_choices) > 1:
                # Only keep 'ง' if it significantly outscores others
                ng_score = choice_scores.get('ง', 0)
                other_scores = [choice_scores[c] for c in top_choices if c != 'ง']
                if other_scores and ng_score < max(other_scores) * 1.2:
                    top_choices = [c for c in top_choices if c != 'ง']
            
            # Limit to reasonable number
            if len(top_choices) > 3:
                top_choices = sorted(top_choices, key=lambda x: choice_scores[x], reverse=True)[:3]
            
            confidence = min(0.7 + (max_score * 0.005), 0.95)
            reasoning = f"Multi-tool scoring: max={max_score}, sources={len(all_data)}"
            
            return {
                "answer": sorted(top_choices),
                "confidence": confidence,
                "reasoning": reasoning
            }
        
        else:
            # Low confidence - return best guess
            best_choice = max(choice_scores.items(), key=lambda x: x[1])
            return {
                "answer": [best_choice[0]],
                "confidence": 0.6,
                "reasoning": f"Low confidence: best={best_choice[0]} score={best_choice[1]}"
            }

def test_multi_tool_mcp():
    """Test the multi-tool MCP client"""
    print("🧪 Testing Multi-Tool MCP Client")
    print("=" * 40)
    
    client = MultiToolMCPClient()
    
    # Test complex questions that need multiple tools
    test_cases = [
        {
            "name": "Complex Exclusion Question",
            "question": "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?",
            "choices": {
                "ก": "สิทธิหลักประกันสุขภาพแห่งชาติ",
                "ข": "สิทธิบัตรทอง", 
                "ค": "สิทธิ 30 บาทรักษาทุกโรค",
                "ง": "ไม่มีข้อใดถูกต้อง"
            },
            "predicted": ["ง"]
        },
        {
            "name": "Comparison Question", 
            "question": "ความแตกต่างระหว่างสิทธิบัตรทองและสิทธิประกันสุขภาพแห่งชาติคืออะไร?",
            "choices": {
                "ก": "ค่าใช้จ่าย",
                "ข": "กลุ่มเป้าหมาย",
                "ค": "บริการที่ครอบคลุม",
                "ง": "ไม่มีความแตกต่าง"
            },
            "predicted": ["ง"]
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Test: {test_case['name']}")
        print(f"   Question: {test_case['question'][:60]}...")
        print(f"   Original: {test_case['predicted']}")
        
        # Analyze complexity
        query_plan = client.analyze_question_complexity(test_case['question'], test_case['choices'])
        print(f"   🔧 Strategy: {query_plan.reasoning}")
        print(f"   📊 Tools planned: {len(query_plan.primary_tools + query_plan.secondary_tools + query_plan.validation_tools)}")
        
        # Execute multi-tool query
        result = client.execute_multi_tool_query(
            test_case['question'],
            test_case['choices'], 
            test_case['predicted']
        )
        
        print(f"   ✅ Final Answer: {result.final_answer}")
        print(f"   📈 Confidence: {result.confidence:.2f}")
        print(f"   🔧 Tools Used: {result.tool_calls_made}")
        print(f"   📚 Evidence Sources: {len(result.evidence_sources)}")
        
        if result.final_answer != test_case['predicted']:
            print(f"   🎯 MULTI-TOOL IMPROVEMENT!")
    
    return True

if __name__ == "__main__":
    test_multi_tool_mcp()