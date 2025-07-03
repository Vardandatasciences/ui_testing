import json
import re
try:
    from langchain_ollama import OllamaLLM
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: langchain_ollama not available, falling back to mock analysis")
import random
import traceback

def analyze_incident_comprehensive(incident_title, incident_description):
    """
    Comprehensive incident analysis for GRC banking system.
    
    Args:
        incident_title (str): Title of the incident
        incident_description (str): Detailed description of the incident
    
    Returns:
        dict: JSON object containing comprehensive incident analysis
    """
    try:
        # Check if Ollama is available
        if not OLLAMA_AVAILABLE:
            print("Ollama not available, using fallback analysis")
            return generate_comprehensive_fallback_analysis(incident_title, incident_description)
            
        # Initialize the local SLM model with increased timeout
        llm = OllamaLLM(model="llama3.2:3b", temperature=0.7, request_timeout=60.0)
       
        prompt_template = PromptTemplate.from_template("""
        You are a senior cybersecurity analyst and risk management expert specializing in banking GRC (Governance, Risk, and Compliance) systems. 
        
        Analyze the following security incident and provide a comprehensive assessment in JSON format with these specific fields:

        1. "riskPriority": Priority level for risk register (P0, P1, P2, P3) where P0 is critical, P1 is high, P2 is medium, P3 is low
        2. "criticality": Severity level (Critical, High, Medium, Low) based on business impact and urgency
        3. "costOfIncident": Estimated financial impact as a STRING (e.g., "$50,000 ,$250,000", "$100,000", "€25,000")
        4. "possibleDamage": Detailed description as a STRING of potential harm including operational, financial, reputational, and regulatory consequences
        5. "systemsInvolved": Array of strings listing specific banking systems, applications, networks, or infrastructure components affected
        6. "initialImpactAssessment": STRING describing immediate assessment of what has been compromised, affected, or at risk
        7. "mitigationSteps": Array of strings with step-by-step actions (do NOT use numbered format like "1.", just plain strings)
        8. "comments": STRING with additional observations, context, or expert insights about the incident
        9. "violatedPolicies": Array of strings listing specific bank policies, procedures, or regulatory requirements violated
        10. "procedureControlFailures": Array of strings listing specific control mechanisms, procedures, or safeguards that failed
        11. "lessonsLearned": Array of strings with key insights, improvements, and preventive measures

        CRITICAL JSON FORMATTING REQUIREMENTS:
        - ALL values must be either strings (in quotes) or arrays of strings
        - Do NOT use numbered lists like "1. text" - use plain strings: "text"
        - Do NOT use objects for costOfIncident or initialImpactAssessment - use simple strings
        - Ensure all arrays contain only strings
        - No trailing commas
        - Valid JSON syntax only
        - IMPORTANT: Do not use escape characters or backslashes in your JSON output

        For banking context, consider:
        - Regulatory compliance (GLBA, BSA/AML, SOX, PCI DSS, FFIEC guidelines)
        - Core banking systems (CBS, payment processing, ATM networks, online banking)
        - Customer data protection and privacy requirements
        - Financial transaction integrity and fraud prevention
        - Business continuity and operational resilience
        - Third-party vendor and supply chain risks
        - Insider threat and privileged access management

        For riskPriority assignment:
        - P0: Immediate threat to critical banking operations, customer data, or regulatory compliance
        - P1: Significant impact on business operations or moderate regulatory exposure
        - P2: Limited business impact with manageable consequences
        - P3: Minor impact with minimal business disruption

        For criticality levels:
        - Critical: Severe impact threatening business continuity, major data breach, or significant regulatory violation
        - High: Substantial impact on operations, moderate data exposure, or compliance concerns
        - Medium: Noticeable impact but manageable with standard procedures
        - Low: Minor impact with minimal business disruption

        For cost estimation, provide a range as a string like "$50,000 - $250,000" considering:
        - Direct incident response costs (personnel, technology, external consultants)
        - Regulatory fines and penalties (can range from $100K to $50M+ for major violations)
        - Business disruption and lost revenue
        - Customer notification and credit monitoring costs
        - Legal and litigation expenses
        - Reputational damage and customer attrition
        - System remediation and security improvements

        IMPORTANT: 
        - Ensure all arrays are properly formatted as JSON arrays of strings
        - Provide specific, actionable content for each field
        - Use banking and GRC terminology throughout
        - Consider both immediate and long-term implications
        - Focus on practical, implementable recommendations
        - DO NOT use escape characters or backslashes in your output

        Incident Title: {title}
        Incident Description: {description}

        Respond ONLY with a valid JSON object containing all the fields above. No additional text or formatting.
        """)
       
        chain = LLMChain(llm=llm, prompt=prompt_template)
       
        # Process the incident
        print(f"Analyzing incident: {incident_title}")
        print(f"Description: {incident_description}")
        response = chain.invoke({"title": incident_title, "description": incident_description})["text"]
        print(f"Raw AI response: {response}")
       
        # Clean and parse the JSON from the response
        try:
            # Remove any extra text before or after the JSON
            json_text = response.strip()
            
            # Handle different response formats
            if json_text.startswith("```json") and json_text.endswith("```"):
                json_text = json_text[7:-3].strip()
            elif json_text.startswith("```") and json_text.endswith("```"):
                json_text = json_text[3:-3].strip()
            elif "```json" in json_text:
                # Extract JSON from markdown code block
                start_idx = json_text.find("```json") + 7
                end_idx = json_text.find("```", start_idx)
                if end_idx != -1:
                    json_text = json_text[start_idx:end_idx].strip()
            elif "{" in json_text and "}" in json_text:
                # Extract JSON object from response
                start_idx = json_text.find("{")
                end_idx = json_text.rfind("}") + 1
                json_text = json_text[start_idx:end_idx]
            
            print(f"Cleaned JSON text: {json_text}")
            
            try:
                # First attempt: Try to parse the JSON directly
                incident_analysis = json.loads(json_text)
            except json.JSONDecodeError as e:
                print(f"Initial JSON parsing failed: {e}")
                
                # Try to fix the JSON by removing problematic backslashes
                try:
                    # Fix the specific issue with escaped backslashes
                    # This is the main issue we're seeing in the logs
                    fixed_json = json_text.replace('\"', '"')
                    
                    # Try to parse the fixed JSON
                    try:
                        incident_analysis = json.loads(fixed_json)
                        print("Successfully parsed JSON after fixing backslashes")
                    except json.JSONDecodeError:
                        # If still failing, try a more aggressive approach
                        print("Still having JSON parsing issues, trying more aggressive fix")
                        
                        # Recreate the JSON from scratch
                        import ast
                        try:
                            # Extract the raw data using regex patterns
                            risk_priority = re.search(r'"riskPriority":\s*"([^"]+)"', json_text)
                            criticality = re.search(r'"criticality":\s*"([^"]+)"', json_text)
                            cost = re.search(r'"costOfIncident":\s*"([^"]+)"', json_text)
                            damage = re.search(r'"possibleDamage":\s*"([^"]+)"', json_text)
                            impact = re.search(r'"initialImpactAssessment":\s*"([^"]+)"', json_text)
                            comments = re.search(r'"comments":\s*"([^"]+)"', json_text)
                            
                            # Create a new clean JSON structure
                            incident_analysis = {
                                "riskPriority": risk_priority.group(1) if risk_priority else "P1",
                                "criticality": criticality.group(1) if criticality else "Medium",
                                "costOfIncident": cost.group(1) if cost else "$50,000 - $250,000",
                                "possibleDamage": damage.group(1) if damage else "Potential data exposure and operational disruption",
                                "systemsInvolved": ["Core Banking System", "Network Infrastructure"],
                                "initialImpactAssessment": impact.group(1) if impact else "Immediate assessment required",
                                "mitigationSteps": [
                                    "Isolate affected systems",
                                    "Notify stakeholders",
                                    "Conduct investigation"
                                ],
                                "comments": comments.group(1) if comments else "Incident requires immediate attention",
                                "violatedPolicies": ["Data Protection Policy", "Security Policy"],
                                "procedureControlFailures": ["Access Control", "Security Monitoring"],
                                "lessonsLearned": ["Improve security controls", "Enhance monitoring"]
                            }
                            print("Created clean JSON structure from regex extraction")
                        except Exception as regex_error:
                            print(f"Regex extraction failed: {regex_error}")
                            # If all else fails, use the fallback
                            return generate_comprehensive_fallback_analysis(incident_title, incident_description)
                except Exception as fix_error:
                    print(f"Failed to fix JSON: {fix_error}")
                    # If parsing still fails, fall back to the generated response
                    print("Falling back to generated analysis")
                    return generate_comprehensive_fallback_analysis(incident_title, incident_description)
            
            # Validate that we have the required fields
            required_fields = ['riskPriority', 'criticality', 'costOfIncident', 'possibleDamage', 
                             'systemsInvolved', 'initialImpactAssessment', 'mitigationSteps', 
                             'comments', 'violatedPolicies', 'procedureControlFailures', 'lessonsLearned']
            missing_fields = [field for field in required_fields if field not in incident_analysis]
            
            if missing_fields:
                print(f"Missing required fields in AI response: {missing_fields}")
                print("Falling back to generated analysis")
                return generate_comprehensive_fallback_analysis(incident_title, incident_description)
            
            print(f"Successfully parsed comprehensive incident analysis: {incident_analysis}")
            return incident_analysis
            
        except Exception as e:
            print(f"JSON parsing error: {e}")
            print(f"Failed to parse JSON from: {json_text}")
            # If JSON parsing fails, fall back to the generated response
            return generate_comprehensive_fallback_analysis(incident_title, incident_description)
            
    except Exception as e:
        print(f"Error using Ollama model: {e}")
        traceback.print_exc()
        # Fall back to a generated response if the model fails
        return generate_comprehensive_fallback_analysis(incident_title, incident_description)

def generate_comprehensive_fallback_analysis(incident_title, incident_description):
    """Generate a comprehensive fallback analysis when the AI model is unavailable."""
    # Extract some keywords from the incident for basic categorization
    description_lower = (incident_title + " " + incident_description).lower()
    
    # Default values
    risk_priority = "P1"
    criticality = "Medium"
    cost_estimate = "$50,000 - $250,000"
    systems = ["Core Banking System", "Network Infrastructure"]
    
    # Basic categorization based on keywords and assign appropriate values
    if any(word in description_lower for word in ["breach", "leak", "exposed", "data", "sensitive", "customer"]):
        risk_priority = "P0"
        criticality = "Critical"
        cost_estimate = "$500,000 - $5,000,000"
        systems = ["Core Banking System", "Customer Database", "Online Banking Platform", "Data Warehouse"]
        possible_damage = "Massive customer data exposure, regulatory penalties up to $50M, severe reputational damage, potential class-action lawsuits, loss of customer trust, and business continuity threats."
        violated_policies = ["Data Protection Policy", "Customer Privacy Policy", "Information Security Policy", "Incident Response Policy"]
        control_failures = ["Data encryption controls", "Access control mechanisms", "Data loss prevention systems", "Network segmentation controls"]
        
    elif any(word in description_lower for word in ["malware", "virus", "ransomware", "trojan", "attack"]):
        risk_priority = "P0"
        criticality = "Critical"
        cost_estimate = "$250,000 - $2,000,000"
        systems = ["Core Banking System", "ATM Network", "Payment Processing System", "Email System"]
        possible_damage = "System disruption, potential data encryption, business operations halt, customer service interruption, and recovery costs."
        violated_policies = ["Malware Protection Policy", "System Security Policy", "Business Continuity Policy"]
        control_failures = ["Antivirus protection", "Email filtering systems", "Network intrusion detection", "Endpoint protection controls"]
        
    elif any(word in description_lower for word in ["phish", "social engineering", "fraud", "impersonation"]):
        risk_priority = "P1"
        criticality = "High"
        cost_estimate = "$100,000 - $750,000"
        systems = ["Email System", "Online Banking Platform", "Employee Workstations", "Authentication System"]
        possible_damage = "Credential theft, unauthorized access to customer accounts, potential financial fraud, and employee security awareness gaps."
        violated_policies = ["Email Security Policy", "Authentication Policy", "Employee Training Policy", "Fraud Prevention Policy"]
        control_failures = ["Email security controls", "Multi-factor authentication", "User awareness training", "Fraud detection systems"]
        
    elif any(word in description_lower for word in ["unauthorized", "access", "privilege", "credential", "insider"]):
        risk_priority = "P1"
        criticality = "High"
        cost_estimate = "$150,000 - $1,000,000"
        systems = ["Core Banking System", "Privileged Access Management", "Active Directory", "Database Systems"]
        possible_damage = "Unauthorized access to sensitive data, privilege escalation, potential data theft, and insider threat materialization."
        violated_policies = ["Access Control Policy", "Privileged Access Policy", "Identity Management Policy", "Segregation of Duties Policy"]
        control_failures = ["Access control systems", "Privilege management controls", "User access reviews", "Segregation of duties controls"]
        
    elif any(word in description_lower for word in ["compliance", "regulatory", "audit", "violation"]):
        risk_priority = "P1"
        criticality = "High"
        cost_estimate = "$200,000 - $10,000,000"
        systems = ["Compliance Management System", "Audit Trail System", "Reporting System", "Document Management"]
        possible_damage = "Regulatory fines, enforcement actions, audit findings, reputational damage, and increased regulatory scrutiny."
        violated_policies = ["Regulatory Compliance Policy", "Audit Policy", "Documentation Policy", "Reporting Policy"]
        control_failures = ["Compliance monitoring controls", "Audit trail mechanisms", "Regulatory reporting controls", "Documentation controls"]
        
    else:
        # Default case
        possible_damage = "Potential operational disruption, security compromise, and moderate business impact requiring immediate attention."
        violated_policies = ["Information Security Policy", "Incident Response Policy", "Risk Management Policy"]
        control_failures = ["Security monitoring controls", "Incident detection systems", "Risk assessment procedures"]
    
    return {
        "riskPriority": risk_priority,
        "criticality": criticality,
        "costOfIncident": cost_estimate,
        "possibleDamage": possible_damage,
        "systemsInvolved": systems,
        "initialImpactAssessment": f"Incident '{incident_title}' has been identified with potential impact on critical banking operations. Immediate containment and investigation required to determine full scope and prevent escalation.",
        "mitigationSteps": [
            "Step 1: Activate incident response team and establish command center",
            "Step 2: Isolate affected systems to prevent further compromise or spread",
            "Step 3: Preserve evidence and maintain chain of custody for forensic analysis",
            "Step 4: Assess immediate business impact and implement business continuity measures",
            "Step 5: Notify key stakeholders including senior management and legal team",
            "Step 6: Conduct preliminary investigation to determine root cause and scope",
            "Step 7: Implement temporary controls and workarounds to restore operations",
            "Step 8: Engage external experts if specialized skills are required",
            "Step 9: Prepare regulatory notifications if required by compliance obligations",
            "Step 10: Document all actions taken and maintain incident timeline",
            "Step 11: Conduct post-incident review and implement lessons learned",
            "Step 12: Update security controls and procedures to prevent recurrence"
        ],
        "comments": f"This incident requires immediate attention due to its potential impact on banking operations. The analysis is based on the incident title '{incident_title}' and available description. Further investigation may reveal additional complexities requiring escalated response measures.",
        "violatedPolicies": violated_policies,
        "procedureControlFailures": control_failures,
        "lessonsLearned": [
            "Importance of rapid incident detection and response capabilities",
            "Need for regular security awareness training and testing",
            "Critical role of backup and recovery procedures in business continuity",
            "Value of comprehensive incident documentation for future reference",
            "Necessity of regular security control testing and validation",
            "Importance of clear communication channels during incident response",
            "Need for regular review and update of incident response procedures",
            "Critical importance of stakeholder notification and regulatory compliance"
        ]
    }
