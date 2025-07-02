"""
Test script for incident_slm.py
"""

from .incident_slm import analyze_incident_comprehensive, generate_comprehensive_fallback_analysis

def test_analyze_incident():
    """Test the analyze_incident_comprehensive function"""
    print("Testing analyze_incident_comprehensive...")
    result = analyze_incident_comprehensive('Test Incident', 'This is a test incident description')
    print(f"Result type: {type(result)}")
    print(f"Result keys: {list(result.keys())}")
    return result

def test_fallback_analysis():
    """Test the generate_comprehensive_fallback_analysis function"""
    print("Testing generate_comprehensive_fallback_analysis...")
    result = generate_comprehensive_fallback_analysis('Test Incident', 'This is a test incident description')
    print(f"Result type: {type(result)}")
    print(f"Result keys: {list(result.keys())}")
    return result

if __name__ == "__main__":
    # Test both functions
    print("=== Testing incident_slm.py ===")
    
    # Test the main analysis function
    main_result = test_analyze_incident()
    
    # Test the fallback analysis function
    fallback_result = test_fallback_analysis()
    
    # Verify the results
    print("\n=== Verification ===")
    print(f"Main analysis returned valid result: {isinstance(main_result, dict)}")
    print(f"Fallback analysis returned valid result: {isinstance(fallback_result, dict)}")
    
    # Check if the required fields are present
    required_fields = [
        'riskPriority', 'criticality', 'costOfIncident', 'possibleDamage', 
        'systemsInvolved', 'initialImpactAssessment', 'mitigationSteps', 
        'comments', 'violatedPolicies', 'procedureControlFailures', 'lessonsLearned'
    ]
    
    main_missing = [field for field in required_fields if field not in main_result]
    fallback_missing = [field for field in required_fields if field not in fallback_result]
    
    print(f"Main analysis missing fields: {main_missing}")
    print(f"Fallback analysis missing fields: {fallback_missing}")
    
    print("\nTest completed successfully!") 