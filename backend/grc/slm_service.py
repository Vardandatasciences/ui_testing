import json
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

def analyze_security_incident(incident_description):
    try:
        # Check if Ollama is available
        if not OLLAMA_AVAILABLE:
            print("Ollama not available, using fallback analysis")
            return generate_fallback_analysis(incident_description)
            
        # Initialize the local SLM model
        llm = OllamaLLM(model="llama3.2:3b", temperature=0.7)
       
        prompt_template = PromptTemplate.from_template("""
        You are a cybersecurity expert specializing in analyzing security incidents for a bank's Governance, Risk, and Compliance (GRC) system.
       
        Analyze the following security incident and provide a comprehensive risk assessment in JSON format with these fields:
       
        1. "criticality": The severity level of the incident (Severe, Significant, Moderate, Minor) - define how serious the incident is to bank operations
        2. "possibleDamage": Potential harm that could result from this incident
        3. "category": The type of security incident (e.g., Data Breach, Malware, Phishing, Unauthorized Access)
        4. "riskDescription": A brief explanation of the risk scenario in cause-effect format (e.g., "If X occurs, then Y happens")
        5. "riskLikelihood": Integer score from 1-10 indicating probability of the risk occurring (1=Very Unlikely, 10=Almost Certain)
        6. "riskLikelihoodJustification": Detailed explanation of why you assigned this specific likelihood score, including factors considered
        7. "riskImpact": Integer score from 1-10 indicating potential consequences (1=Negligible Impact, 10=Catastrophic Impact)
        8. "riskImpactJustification": Detailed explanation of why you assigned this specific impact score, including potential damages and consequences
        9. "riskExposureRating": Overall calculation of risk exposure based on likelihood and impact (Critical Exposure, High Exposure, Elevated Exposure, Low Exposure) - combined rating showing total risk posture
        10. "riskPriority": Relative indicator of criticality in the risk register (P0, P1, P2, P3)
        11. "riskAppetite": Assessment of whether this risk falls within the bank's acceptable tolerance levels (Within Appetite, Borderline, Exceeds Appetite) with consideration of regulatory thresholds, capital requirements, and operational risk frameworks
        12. "riskMitigation": Array of numbered step-by-step actions to resolve and mitigate this incident, specifically for banking environments
       
        For riskLikelihood (1-10 scale):
        - 1-2: Very Unlikely (rare occurrence, multiple safeguards in place)
        - 3-4: Unlikely (some protective measures, but vulnerabilities exist)
        - 5-6: Possible (moderate probability, some risk factors present)
        - 7-8: Likely (high probability, significant risk factors)
        - 9-10: Almost Certain (imminent threat, critical vulnerabilities exposed)
        
        For riskImpact (1-10 scale):
        - 1-2: Negligible (minimal business disruption, easily recoverable)
        - 3-4: Minor (limited impact, some operational disruption)
        - 5-6: Moderate (significant impact, noticeable business disruption)
        - 7-8: Major (severe impact, substantial financial/operational consequences)
        - 9-10: Catastrophic (devastating impact, threatens business continuity)
       
        Use banking and GRC terminology throughout your analysis. Consider regulatory compliance requirements (e.g., GLBA, BSA/AML), financial impact, reputational damage, customer trust implications, and required regulatory reporting.
       
        IMPORTANT: 
        - Ensure riskLikelihood and riskImpact are integers between 1-10
        - Provide detailed justifications for both scores
        - Ensure the "riskMitigation" field is formatted as a proper JSON array of strings
       
        Security Incident Details:
        {incident}
       
        Respond ONLY with a valid JSON object containing the fields above.
        """)
       
        chain = LLMChain(llm=llm, prompt=prompt_template)
       
        # Process the incident
        print(f"Sending incident to AI: {incident_description}")
        response = chain.invoke({"incident": incident_description})["text"]
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
            incident_analysis = json.loads(json_text)
            
            # Validate that we have the required fields
            required_fields = ['riskLikelihood', 'riskImpact', 'riskLikelihoodJustification', 'riskImpactJustification']
            missing_fields = [field for field in required_fields if field not in incident_analysis]
            
            if missing_fields:
                print(f"Missing required fields in AI response: {missing_fields}")
                print("Falling back to generated analysis")
                return generate_fallback_analysis(incident_description)
            
            # Ensure likelihood and impact are integers
            if 'riskLikelihood' in incident_analysis:
                try:
                    incident_analysis['riskLikelihood'] = int(incident_analysis['riskLikelihood'])
                except (ValueError, TypeError):
                    incident_analysis['riskLikelihood'] = 5
            
            if 'riskImpact' in incident_analysis:
                try:
                    incident_analysis['riskImpact'] = int(incident_analysis['riskImpact'])
                except (ValueError, TypeError):
                    incident_analysis['riskImpact'] = 5
            
            print(f"Successfully parsed AI analysis: {incident_analysis}")
            return incident_analysis
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Failed to parse JSON from: {json_text}")
            # If JSON parsing fails, fall back to the generated response
            return generate_fallback_analysis(incident_description)
            
    except Exception as e:
        print(f"Error using Ollama model: {e}")
        traceback.print_exc()
        # Fall back to a generated response if the model fails
        return generate_fallback_analysis(incident_description)

def generate_fallback_analysis(incident_description):
    """Generate a fallback analysis when the AI model is unavailable."""
    # Extract some keywords from the incident for basic categorization
    description_lower = incident_description.lower()
    
    # Default values
    criticality = "Significant"
    category = "IT Security"
    likelihood_score = 5
    impact_score = 5
    priority = "P1"
    
    # Basic categorization based on keywords and assign appropriate scores
    if any(word in description_lower for word in ["breach", "leak", "exposed", "data", "sensitive"]):
        category = "Data Breach"
        criticality = "Severe"
        likelihood_score = 7
        impact_score = 8
        priority = "P0"
        likelihood_justification = "Data breaches have high likelihood due to increasing cyber threats and the valuable nature of banking data. Score of 7 reflects significant threat landscape."
        impact_justification = "Data breaches can cause severe financial losses, regulatory penalties, and reputational damage. Score of 8 reflects major consequences for banking operations."
    elif any(word in description_lower for word in ["malware", "virus", "ransomware", "trojan"]):
        category = "Malware"
        criticality = "Severe"
        likelihood_score = 6
        impact_score = 8
        likelihood_justification = "Malware attacks are moderately likely given current threat environment and banking sector targeting. Score of 6 reflects ongoing risk."
        impact_justification = "Malware can disrupt critical banking systems, encrypt data, and halt operations. Score of 8 reflects severe operational impact."
    elif any(word in description_lower for word in ["phish", "social engineering", "impersonation"]):
        category = "Phishing"
        likelihood_score = 7
        impact_score = 6
        likelihood_justification = "Phishing attacks are highly likely as they target human vulnerabilities and are easy to execute. Score of 7 reflects frequent occurrence."
        impact_justification = "Phishing can lead to credential theft and unauthorized access but impact is more limited. Score of 6 reflects moderate consequences."
    elif any(word in description_lower for word in ["unauthorized", "access", "privilege", "credential"]):
        category = "Unauthorized Access"
        likelihood_score = 6
        impact_score = 7
        likelihood_justification = "Unauthorized access attempts are moderately likely given credential-based attacks. Score of 6 reflects consistent threat level."
        impact_justification = "Unauthorized access can compromise sensitive data and systems integrity. Score of 7 reflects significant potential damage."
    elif any(word in description_lower for word in ["ddos", "denial", "service", "availability"]):
        category = "Denial of Service"
        likelihood_score = 5
        impact_score = 6
        likelihood_justification = "DDoS attacks have moderate likelihood, often used for distraction or service disruption. Score of 5 reflects balanced risk."
        impact_justification = "Service denial can disrupt customer access and operations but recovery is usually possible. Score of 6 reflects moderate impact."
    elif any(word in description_lower for word in ["compliance", "regulatory", "regulation"]):
        category = "Compliance"
        likelihood_score = 4
        impact_score = 7
        likelihood_justification = "Compliance violations have lower likelihood with proper controls but regulatory changes increase risk. Score of 4 reflects controlled environment."
        impact_justification = "Compliance violations can result in significant fines and regulatory sanctions. Score of 7 reflects serious consequences."
    else:
        # Default case
        likelihood_justification = "General security incident with moderate likelihood based on current threat landscape. Score of 5 reflects balanced assessment."
        impact_justification = "Potential impact is moderate considering banking sector criticality and customer data sensitivity. Score of 5 reflects standard risk level."
    
    # Extract a title if possible
    title_match = None
    if "Title:" in incident_description:
        title_parts = incident_description.split("Title:", 1)[1].split("\n", 1)
        if title_parts:
            title_match = title_parts[0].strip()
    
    title = title_match or "Security Incident"
    
    return {
        "criticality": criticality,
        "possibleDamage": "Potential data exposure, system compromise, and reputational damage to the organization.",
        "category": category,
        "riskDescription": f"If this {category.lower()} incident is not properly addressed, it may lead to unauthorized access to sensitive data, financial loss, and regulatory penalties.",
        "riskLikelihood": likelihood_score,
        "riskLikelihoodJustification": likelihood_justification,
        "riskImpact": impact_score,
        "riskImpactJustification": impact_justification,
        "riskExposureRating": "High Exposure",
        "riskPriority": priority,
        "riskAppetite": "Exceeds Appetite",
        "riskMitigation": [
            "Step 1: Isolate affected systems to prevent further compromise",
            "Step 2: Initiate incident response procedures according to the security policy",
            "Step 3: Notify relevant stakeholders and regulatory bodies if required",
            "Step 4: Perform forensic analysis to determine the extent of the breach",
            "Step 5: Implement remediation actions to address the vulnerability",
            "Step 6: Update security controls to prevent similar incidents",
            "Step 7: Conduct post-incident review and update documentation"
        ]
    } 
