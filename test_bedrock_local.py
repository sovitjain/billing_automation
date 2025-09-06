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
            print(f"✓ Loaded clinical notes: {len(clinical_notes)} characters")
            
            # Add Commercial plan prefix
            notes_with_prefix = f"Commercial plan: {clinical_notes}"
            print(f"✓ Added Commercial plan prefix: {len(notes_with_prefix)} characters")
            
        except Exception as e:
            print(f"✗ Error reading clinical notes: {e}")
            print("Make sure 'final_clinical_notes_for_bedrock.txt' exists in current directory")
            return False
        
        # Step 2: Read prompt from prompt.txt
        print("\nStep 2: Loading prompt template...")
        try:
            prompt_template = bedrock_cpt_predictor.read_text_file('prompt.txt')
            print(f"✓ Loaded prompt template: {len(prompt_template)} characters")
        except Exception as e:
            print(f"✗ Error reading prompt: {e}")
            print("Using default prompt")
            prompt_template = bedrock_cpt_predictor.get_default_prompt()
        
        # Step 3: Get AWS region from config
        aws_region = config.get('DEFAULT', 'aws_region', fallback='us-east-1')
        print(f"✓ AWS Region: {aws_region}")
        
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
        min_expected_codes = 4  # Commercial plan should have at least 4 CPT codes
        
        for attempt in range(max_retries):
            print(f"Bedrock attempt {attempt + 1}/{max_retries}")
            
            predicted_codes_text = bedrock_cpt_predictor.get_cpt_codes_from_bedrock(
                notes=notes_with_prefix,
                prompt_template=prompt_template,
                region=aws_region
            )
            
            if not predicted_codes_text:
                print(f"✗ Attempt {attempt + 1}: No response from Bedrock")
                continue
            
            # Quick check - parse and count codes
            temp_parsed = bedrock_cpt_predictor.parse_json_response(predicted_codes_text)
            code_count = 0
            
            if temp_parsed:
                if isinstance(temp_parsed, list):
                    code_count = len(temp_parsed)
                elif isinstance(temp_parsed, dict):
                    if 'cpt_codes' in temp_parsed:
                        code_count = len(temp_parsed['cpt_codes'])
                    elif 'codes' in temp_parsed:
                        code_count = len(temp_parsed['codes'])
            
            print(f"Attempt {attempt + 1}: Received {code_count} CPT codes")
            
            # Check if we have enough codes
            if code_count >= min_expected_codes:
                print(f"✓ Received sufficient CPT codes ({code_count})")
                break
            elif code_count > 0:
                print(f"⚠ Only received {code_count} codes, expected at least {min_expected_codes}")
                if attempt < max_retries - 1:
                    print("Retrying with enhanced prompt...")
                    # Add emphasis to the prompt for retry
                    enhanced_prompt = prompt_template + f"\n\nIMPORTANT: For Commercial plan, you MUST provide at least {min_expected_codes} CPT codes. Always include 99213 for office visit. If you only provided {code_count} codes, please add the missing codes."
                    prompt_template = enhanced_prompt
                else:
                    print(f"Using result with {code_count} codes (all retries exhausted)")
            else:
                print(f"✗ Attempt {attempt + 1}: No valid codes parsed")
                if attempt < max_retries - 1:
                    print("Retrying...")
        
        if not predicted_codes_text:
            print("✗ All Bedrock attempts failed")
            return False
        
        print(f"✓ Bedrock response received: {len(predicted_codes_text)} characters")
        
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
                print("✓ Found direct array format")
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
                print(f"✓ Successfully parsed {len(cpt_codes)} CPT codes from Bedrock response")
                
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
                    print("✓ Results saved to 'bedrock_test_results.json'")
                except Exception as save_error:
                    print(f"⚠ Could not save results: {save_error}")
                
                print("=" * 60)
                print("✓ BEDROCK TEST COMPLETED SUCCESSFULLY")
                print("=" * 60)
                return True
            else:
                print("✗ No valid CPT codes found in response")
                return False
        else:
            print("✗ Could not parse JSON response from Bedrock")
            print(f"Raw response: {predicted_codes_text}")
            return False
            
    except Exception as e:
        print(f"✗ Error during Bedrock testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Bedrock CPT Predictor Local Test")
    print("This script tests the Bedrock prediction using:")
    print("- final_clinical_notes_for_bedrock.txt (clinical notes)")
    print("- prompt.txt (prompt template)")
    print("- config.properties (AWS configuration)")
    print()
    
    # Check if required files exist
    required_files = [
        'final_clinical_notes_for_bedrock.txt',
        'prompt.txt',
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
        print("✗ Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nPlease ensure all required files are in the current directory.")
        sys.exit(1)
    
    print("✓ All required files found")
    print()
    
    # Run the test
    success = test_bedrock_prediction()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("Check 'bedrock_test_results.json' for the parsed CPT codes.")
    else:
        print("\n❌ Test failed!")
        print("Check the error messages above for troubleshooting.")
    
    sys.exit(0 if success else 1)