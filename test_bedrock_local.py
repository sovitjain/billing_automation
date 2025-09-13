#!/usr/bin/env python3
"""
Test Bedrock CPT Predictor Locally
Tests the bedrock_cpt_predictor module using final_clinical_notes_for_bedrock.txt and prompt.txt
"""

import sys
import json
import configparser

# Import the bedrock CPT predictor module
try:
    import bedrock_cpt_predictor
    print("Successfully imported bedrock_cpt_predictor module")
except ImportError as e:
    print(f"Error importing bedrock_cpt_predictor: {e}")
    print("Make sure bedrock_cpt_predictor.py is in the same directory")
    sys.exit(1)

def load_config():
    """Load configuration from config.properties"""
    config = configparser.ConfigParser()
    config.read('config.properties')
    return config

def debug_manometry_status(clinical_notes):
    """
    Debug function to check whether anorectal manometry was performed or deferred
    Based on prompt.txt rules: Remove cpt 91122 if Anorectal manometry was not done, deferred, cancelled, or unavailable
    """
    print("=" * 60)
    print("DEBUG: DEBUG: ANORECTAL MANOMETRY STATUS CHECK")
    print("=" * 60)
    
    # Convert to lowercase for case-insensitive matching
    notes_lower = clinical_notes.lower()
    
    # Keywords that indicate manometry was deferred/not done/cancelled/unavailable
    negative_keywords = [
        'anorectal manometry was deferred',
        'anorectal manometry deferred',
        'manometry was deferred',
        'manometry deferred',
        'anorectal manometry was not done',
        'anorectal manometry not done',
        'manometry was not done',
        'manometry not done',
        'anorectal manometry was cancelled',
        'anorectal manometry cancelled',
        'manometry was cancelled',
        'manometry cancelled',
        'anorectal manometry was unavailable',
        'anorectal manometry unavailable',
        'manometry was unavailable',
        'manometry unavailable'
    ]
    
    # Keywords that indicate manometry was performed
    positive_keywords = [
        'anorectal manometry is performed',
        'anorectal manometry was performed',
        'anorectal manometry performed',
        'manometry is performed',
        'manometry was performed',
        'manometry performed',
        'anal pressure probe is used',
        'anal pressure probe was used',
        'anal pressure record'
    ]
    
    # Check for negative indicators first
    deferred_found = False
    deferred_match = ""
    for keyword in negative_keywords:
        if keyword in notes_lower:
            deferred_found = True
            deferred_match = keyword
            break
    
    # Check for positive indicators
    performed_found = False
    performed_match = ""
    for keyword in positive_keywords:
        if keyword in notes_lower:
            performed_found = True
            performed_match = keyword
            break
    
    print(f"INFO: Clinical Notes Length: {len(clinical_notes)} characters")
    print(f"DEBUG: Searching for manometry status indicators...")
    print()
    
    # Show the result
    if deferred_found and not performed_found:
        print("RESULT: RESULT: Anorectal manometry was DEFERRED/NOT DONE")
        print(f"   Found keyword: '{deferred_match}'")
        print("   FAILED: CPT Code 91122 should be REMOVED")
        print("   Reason: Manometry was not performed")
    elif performed_found and not deferred_found:
        print("SUCCESS: RESULT: Anorectal manometry was PERFORMED")
        print(f"   Found keyword: '{performed_match}'")
        print("   SUCCESS: CPT Code 91122 should be KEPT")
        print("   Reason: Manometry was successfully performed")
    elif deferred_found and performed_found:
        print("WARNING:  RESULT: CONFLICTING INFORMATION FOUND")
        print(f"   Deferred keyword: '{deferred_match}'")
        print(f"   Performed keyword: '{performed_match}'")
        print("   NOTE: MANUAL REVIEW REQUIRED")
        print("   Recommendation: Check clinical notes manually")
    else:
        print("UNKNOWN: RESULT: NO CLEAR MANOMETRY STATUS FOUND")
        print("   No specific keywords found for performed/deferred status")
        print("   NOTE: MANUAL REVIEW REQUIRED")
        print("   Recommendation: Check clinical notes for manometry details")
    
    print("=" * 60)
    
    # Also show a snippet of the notes around any found keywords
    if deferred_found or performed_found:
        keyword = deferred_match if deferred_found else performed_match
        keyword_pos = notes_lower.find(keyword)
        if keyword_pos != -1:
            start = max(0, keyword_pos - 100)
            end = min(len(clinical_notes), keyword_pos + len(keyword) + 100)
            snippet = clinical_notes[start:end]
            print("SNIPPET: RELEVANT SNIPPET FROM CLINICAL NOTES:")
            print("-" * 40)
            print(f"...{snippet}...")
            print("-" * 40)
            print()

def test_bedrock_prediction():
    """Test Bedrock CPT prediction using local files"""
    print("=" * 80)
    print("TESTING BEDROCK CPT PREDICTOR LOCALLY")
    print("=" * 80)
    
    try:
        # Load configuration
        config = load_config()
        
        # Step 1: Read clinical notes from final_clinical_notes_for_bedrock.txt
        print("\nStep 1: Loading clinical notes...")
        try:
            clinical_notes = bedrock_cpt_predictor.read_text_file('final_clinical_notes_for_bedrock.txt')
            print(f"SUCCESS: Loaded clinical notes: {len(clinical_notes)} characters")
            
            # Get insurance plan from config and add prefix
            insurance_plan = config.get('CLAIMS', 'insurance_plan', fallback='Commercial')
            notes_with_prefix = f"{insurance_plan} plan: {clinical_notes}"
            print(f"SUCCESS: Added {insurance_plan} plan prefix: {len(notes_with_prefix)} characters")
            
        except Exception as e:
            print(f"ERROR: Error reading clinical notes: {e}")
            print("Make sure 'final_clinical_notes_for_bedrock.txt' exists in current directory")
            return False
        
        # Step 2: Read prompt from prompt.txt
        print("\nStep 2: Loading prompt template...")
        try:
            # Try insurance-specific prompt file first
            prompt_file = f'prompt_{insurance_plan.lower()}.txt'
            prompt_template = bedrock_cpt_predictor.read_text_file(prompt_file)
            print(f"SUCCESS: Loaded {insurance_plan}-specific prompt from {prompt_file}: {len(prompt_template)} characters")
        except:
            try:
                # Fallback to generic prompt.txt
                prompt_template = bedrock_cpt_predictor.read_text_file('prompt.txt')
                # Replace the generic "Commercial or Medicare plan" with the specific insurance plan
                prompt_template = prompt_template.replace("Commercial or Medicare plan", f"{insurance_plan} plan")
                print(f"SUCCESS: Loaded generic prompt from prompt.txt and customized for {insurance_plan} plan: {len(prompt_template)} characters")
            except Exception as e:
                print(f"ERROR: Error reading prompt: {e}")
                print("Using default prompt")
                prompt_template = bedrock_cpt_predictor.get_default_prompt()
        
        # Step 3: Get AWS region from config
        aws_region = config.get('DEFAULT', 'aws_region', fallback='us-east-1')
        print(f"SUCCESS: AWS Region: {aws_region}")
        
        # Step 4: Show what will be sent to Bedrock
        print("\n" + "=" * 60)
        print("CLINICAL NOTES TO BE SENT TO BEDROCK:")
        print("=" * 60)
        print(notes_with_prefix[:1000] + ("..." if len(notes_with_prefix) > 1000 else ""))
        print("=" * 60)
        
        print("\n" + "=" * 60)
        print("PROMPT TEMPLATE:")
        print("=" * 60)
        print(prompt_template[:500] + ("..." if len(prompt_template) > 500 else ""))
        print("=" * 60)
        
        # Step 5: Call Bedrock API with retry logic
        print("\nStep 5: Calling Bedrock API...")
        print("This may take a few seconds...")
        
        max_retries = 3
        # Set minimum expected codes based on insurance plan
        if insurance_plan.lower() == 'commercial':
            min_expected_codes = 4  # Commercial plan should have at least 4 CPT codes
        else:  # Medicare or other plans
            min_expected_codes = 3  # Medicare typically has fewer codes
        
        for attempt in range(max_retries):
            print(f"Bedrock attempt {attempt + 1}/{max_retries}")
            
            predicted_codes_text = bedrock_cpt_predictor.get_cpt_codes_from_bedrock(
                notes=notes_with_prefix,
                prompt_template=prompt_template,
                region=aws_region
            )
            
            if not predicted_codes_text:
                print(f"ERROR: Attempt {attempt + 1}: No response from Bedrock")
                continue
            
            # Quick check - parse and count codes, also check for missing CPT code fields
            temp_parsed = bedrock_cpt_predictor.parse_json_response(predicted_codes_text)
            code_count = 0
            missing_cpt_codes = 0
            
            if temp_parsed:
                if isinstance(temp_parsed, list):
                    code_count = len(temp_parsed)
                    # Check each item for missing 'code' field
                    for item in temp_parsed:
                        if isinstance(item, dict):
                            cpt_code_value = item.get('cpt') or item.get('cptCode') or item.get('code') or ''
                            if not str(cpt_code_value).strip():
                                missing_cpt_codes += 1
                elif isinstance(temp_parsed, dict):
                    if 'cpt_codes' in temp_parsed:
                        code_list = temp_parsed['cpt_codes']
                        code_count = len(code_list)
                        for item in code_list:
                            if isinstance(item, dict):
                                cpt_code_value = item.get('cpt') or item.get('cptCode') or item.get('code') or ''
                                if not str(cpt_code_value).strip():
                                    missing_cpt_codes += 1
                    elif 'codes' in temp_parsed:
                        code_list = temp_parsed['codes']
                        code_count = len(code_list)
                        for item in code_list:
                            if isinstance(item, dict):
                                cpt_code_value = item.get('cpt') or item.get('cptCode') or item.get('code') or ''
                                if not str(cpt_code_value).strip():
                                    missing_cpt_codes += 1
            
            print(f"Attempt {attempt + 1}: Received {code_count} CPT codes, {missing_cpt_codes} missing CPT code values")
            
            # Check if we have enough codes and no missing CPT code fields
            if code_count >= min_expected_codes and missing_cpt_codes == 0:
                print(f"SUCCESS: Received sufficient CPT codes ({code_count}) with all code fields populated")
                break
            elif missing_cpt_codes > 0:
                print(f"WARNING: {missing_cpt_codes} CPT entries are missing code values")
                if attempt < max_retries - 1:
                    print("Retrying with enhanced prompt for missing CPT codes...")
                    # Add emphasis to the prompt for retry
                    enhanced_prompt = prompt_template + f"\n\nCRITICAL: {missing_cpt_codes} CPT entries are missing the 'code' field. You MUST include valid CPT code numbers (like 99213, 91122, etc.) in the 'code' field for each entry. Do not leave any 'code' fields empty or null."
                    prompt_template = enhanced_prompt
                else:
                    print(f"Using result with {missing_cpt_codes} missing CPT code values (all retries exhausted)")
            elif code_count > 0:
                print(f"WARNING: Only received {code_count} codes, expected at least {min_expected_codes}")
                if attempt < max_retries - 1:
                    print("Retrying with enhanced prompt...")
                    # Add emphasis to the prompt for retry
                    enhanced_prompt = prompt_template + f"\n\nIMPORTANT: For {insurance_plan} plan, you MUST provide at least {min_expected_codes} CPT codes. Always include 99213 for office visit. If you only provided {code_count} codes, please add the missing codes."
                    prompt_template = enhanced_prompt
                else:
                    print(f"Using result with {code_count} codes (all retries exhausted)")
            else:
                print(f"ERROR: Attempt {attempt + 1}: No valid codes parsed")
                if attempt < max_retries - 1:
                    print("Retrying...")
        
        if not predicted_codes_text:
            print("ERROR: All Bedrock attempts failed")
            return False
        
        print(f"SUCCESS: Bedrock response received: {len(predicted_codes_text)} characters")
        
        # Step 5.5: Debug - Check anorectal manometry status
        print("\nStep 5.5: Checking anorectal manometry status...")
        debug_manometry_status(notes_with_prefix)
        
        # Step 6: Parse and display results
        print("\nStep 6: Parsing Bedrock response...")
        print("=" * 60)
        print("RAW BEDROCK RESPONSE:")
        print("=" * 60)
        print(predicted_codes_text)
        print("=" * 60)
        
        # Parse JSON response
        parsed_json = bedrock_cpt_predictor.parse_json_response(predicted_codes_text)
        
        if parsed_json:
            cpt_codes = []
            
            # Handle direct array format (most common)
            if isinstance(parsed_json, list):
                print("SUCCESS: Found direct array format")
                for item in parsed_json:
                    # Handle multiple possible key names for CPT code
                    cpt_code_value = item.get('cpt') or item.get('cptCode') or item.get('code') or ''
                    
                    converted_item = {
                        'code': cpt_code_value,
                        'modifier1': item.get('modifier1', ''),
                        'modifier2': item.get('modifier2', ''),
                        'description': item.get('description', '')
                    }
                    cpt_codes.append(converted_item)
            
            # Handle object with nested array
            elif isinstance(parsed_json, dict):
                if 'cpt_codes' in parsed_json:
                    cpt_codes = parsed_json['cpt_codes']
                elif 'codes' in parsed_json:
                    cpt_codes = parsed_json['codes']
            
            if cpt_codes and len(cpt_codes) > 0:
                print(f"SUCCESS: Successfully parsed {len(cpt_codes)} CPT codes from Bedrock response")
                
                # Display the codes
                print("\n" + "=" * 60)
                print("PREDICTED CPT CODES:")
                print("=" * 60)
                for i, cpt in enumerate(cpt_codes, 1):
                    code = cpt.get('code', 'N/A')
                    print(f"{i}. CPT: {code}")
                    if cpt.get('modifier1'):
                        print(f"   Modifier1: {cpt['modifier1']}")
                    if cpt.get('modifier2'):
                        print(f"   Modifier2: {cpt['modifier2']}")
                    if cpt.get('description'):
                        print(f"   Description: {cpt['description']}")
                    print()
                
                # Save results to file
                try:
                    with open('bedrock_test_results.json', 'w') as f:
                        json.dump(cpt_codes, f, indent=2)
                    print("SUCCESS: Results saved to 'bedrock_test_results.json'")
                except Exception as save_error:
                    print(f"WARNING: Could not save results: {save_error}")
                
                print("=" * 60)
                print("SUCCESS: BEDROCK TEST COMPLETED SUCCESSFULLY")
                print("=" * 60)
                return True
            else:
                print("ERROR: No valid CPT codes found in response")
                return False
        else:
            print("ERROR: Could not parse JSON response from Bedrock")
            print(f"Raw response: {predicted_codes_text}")
            return False
            
    except Exception as e:
        print(f"ERROR: Error during Bedrock testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Bedrock CPT Predictor Local Test")
    
    # Load config to determine which prompt file will be used
    try:
        config = load_config()
        insurance_plan = config.get('CLAIMS', 'insurance_plan', fallback='Commercial')
        prompt_file = f'prompt_{insurance_plan.lower()}.txt'
        
        print("This script tests the Bedrock prediction using:")
        print("- final_clinical_notes_for_bedrock.txt (clinical notes)")
        print(f"- {prompt_file} (insurance-specific prompt template)")
        print("- config.properties (AWS configuration)")
    except:
        print("This script tests the Bedrock prediction using:")
        print("- final_clinical_notes_for_bedrock.txt (clinical notes)")
        print("- prompt.txt (fallback prompt template)")
        print("- config.properties (AWS configuration)")
        insurance_plan = 'Commercial'
        prompt_file = 'prompt_commercial.txt'
    
    print()
    
    # Check if required files exist
    required_files = [
        'final_clinical_notes_for_bedrock.txt',
        prompt_file,
        'config.properties',
        'bedrock_cpt_predictor.py'
    ]
    
    missing_files = []
    for file in required_files:
        try:
            with open(file, 'r'):
                pass
        except FileNotFoundError:
            missing_files.append(file)
    
    if missing_files:
        print("ERROR: Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nPlease ensure all required files are in the current directory.")
        sys.exit(1)
    
    print("SUCCESS: All required files found")
    print()
    
    # Run the test
    success = test_bedrock_prediction()
    
    if success:
        print("\nSUCCESS: Test completed successfully!")
        print("Check 'bedrock_test_results.json' for the parsed CPT codes.")
    else:
        print("\nFAILED: Test failed!")
        print("Check the error messages above for troubleshooting.")
    
    sys.exit(0 if success else 1)