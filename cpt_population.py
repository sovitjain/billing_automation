import sys
import traceback

# Import our bedrock CPT predictor module
try:
    import bedrock_cpt_predictor
    print("Successfully imported bedrock_cpt_predictor module")
except ImportError as e:
    print(f"Error importing bedrock_cpt_predictor: {e}")
    print("Make sure bedrock_cpt_predictor.py is in the same directory")
    sys.exit(1)

def get_predicted_cpt_codes(config):
    """Get CPT codes from Bedrock predictor"""
    print("\n" + "=" * 50)
    print("GETTING CPT CODE PREDICTIONS FROM BEDROCK")
    print("=" * 50)
    
    try:
        # Read notes from notes.txt
        try:
            notes = bedrock_cpt_predictor.read_text_file('notes.txt')
            print(f"Loaded notes from notes.txt ({len(notes)} characters)")
        except Exception as e:
            print(f"Error reading notes.txt: {e}")
            return None
        
        # Read prompt from prompt.txt (with fallback to default)
        try:
            bedrock_prompt = bedrock_cpt_predictor.read_text_file('prompt.txt')
            print("Loaded custom prompt from prompt.txt")
        except:
            bedrock_prompt = bedrock_cpt_predictor.get_default_prompt()
            print("Using default prompt")
        
        # Get AWS region from config
        aws_region = config.get('DEFAULT', 'aws_region', fallback='us-east-1')
        
        # Get predictions from Bedrock
        print("Calling Bedrock API...")
        predicted_codes_text = bedrock_cpt_predictor.get_cpt_codes_from_bedrock(
            notes=notes,
            prompt_template=bedrock_prompt,
            region=aws_region
        )
        
        if not predicted_codes_text:
            print("No response from Bedrock")
            return None
        
        print(f"Bedrock response received: {len(predicted_codes_text)} characters")
        
        # Parse JSON response
        parsed_json = bedrock_cpt_predictor.parse_json_response(predicted_codes_text)
        
        if parsed_json:
            cpt_codes = []
            
            # Handle direct array format (most common)
            if isinstance(parsed_json, list):
                print("Found direct array format")
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
                print(f"Successfully parsed {len(cpt_codes)} CPT codes from Bedrock response")
                
                # Display the codes
                print("\nPREDICTED CPT CODES:")
                print("-" * 30)
                for i, cpt in enumerate(cpt_codes, 1):
                    code = cpt.get('code', 'N/A')
                    print(f"{i}. CPT: {code}")
                    if cpt.get('modifier1'):
                        print(f"   Modifier1: {cpt['modifier1']}")
                    if cpt.get('modifier2'):
                        print(f"   Modifier2: {cpt['modifier2']}")
                    if cpt.get('description'):
                        print(f"   Description: {cpt['description']}")
                
                return cpt_codes
            else:
                print("No valid CPT codes found in response")
                return None
        else:
            print("Could not parse JSON response from Bedrock")
            print(f"Raw response: {predicted_codes_text}")
            return None
            
    except Exception as e:
        print(f"Error getting CPT predictions: {e}")
        traceback.print_exc()
        return None

def close_any_dialogs(page):
    """Close any open dialogs"""
    try:
        dialog_close_selectors = [
            'button:has-text("×")',
            '.close',
            '.modal-close',
            '[aria-label="Close"]',
            'button[aria-label="Close"]',
            'button.close'
        ]
        
        for close_selector in dialog_close_selectors:
            try:
                close_btn = page.locator(close_selector).first
                if close_btn.is_visible():
                    print(f"Closing dialog with: {close_selector}")
                    close_btn.click()
                    page.wait_for_timeout(1000)
                    return True
            except:
                continue
        return False
    except:
        return False

def add_cpt_codes_to_ecw_interface(page, cpt_codes):
    """Add all CPT codes using the * row - Tab creates new rows automatically"""
    if not cpt_codes:
        print("No CPT codes to add")
        return
    
    print(f"\nAdding {len(cpt_codes)} CPT codes to ECW Claims interface...")
    print("Note: Using * row for each CPT code, Tab will auto-create new rows")
    
    try:
        # Take screenshot before starting
        page.screenshot(path="before_cpt_population.png")
        print("Screenshot saved: before_cpt_population.png")
        
        # Process ALL CPT codes starting from the first one (99213)
        for i in range(len(cpt_codes)):
            cpt_data = cpt_codes[i]
            cpt_code = cpt_data.get('code', '')
            modifier1 = cpt_data.get('modifier1', '')
            modifier2 = cpt_data.get('modifier2', '')
            
            print(f"\nProcessing CPT code {i+1}: {cpt_code}")
            if modifier1:
                print(f"  - Modifier1: {modifier1}")
            if modifier2:
                print(f"  - Modifier2: {modifier2}")
            
            if i == 0:
                print("First CPT code (99213) - adding to * row")
            else:
                print("Additional CPT code - Tab will create new row automatically")
            
            # Close any open dialogs first
            close_any_dialogs(page)
            
            # Always use the * row (newCPT field) - it should be available for each iteration
            try:
                # Look for the newCPT field (the * row)
                code_field_selectors = [
                    'input[ng-model="newCPT"]',
                    '#billingClaimIpt34'
                ]
                
                code_field_found = False
                for selector in code_field_selectors:
                    try:
                        code_field = page.locator(selector).first
                        
                        if code_field.is_visible() and code_field.is_enabled():
                            print(f"Found * row CPT field: {selector}")
                            
                            # Highlight the field
                            code_field.evaluate("element => element.style.border = '3px solid green'")
                            page.wait_for_timeout(1000)
                            
                            # Click and clear the field
                            code_field.click()
                            page.wait_for_timeout(300)
                            code_field.evaluate("element => element.value = ''")
                            
                            # Type the CPT code slowly
                            page.keyboard.type(cpt_code, delay=150)
                            print(f"Entered CPT code: {cpt_code}")
                            
                            # Remove highlight
                            code_field.evaluate("element => element.style.border = ''")
                            
                            # Tab to trigger auto-population AND create new row
                            print("Pressing Tab to save CPT code and auto-create next row...")
                            page.keyboard.press('Tab')
                            page.wait_for_timeout(4000)  # Wait for row creation
                            
                            code_field_found = True
                            break
                            
                    except Exception as e:
                        print(f"Selector {selector} failed: {e}")
                        continue
                
                if not code_field_found:
                    print(f"Could not find * row field for CPT code {cpt_code}")
                    page.screenshot(path=f"debug_no_star_row_{i+1}.png")
                    continue
                
                # Now add modifiers to the row that was just created/populated
                current_row = i + 1  # The row number where this CPT code now exists
                print(f"Adding modifiers to row {current_row} for CPT {cpt_code}")
                
                # Add M1 modifier if present
                if modifier1:
                    print(f"Adding M1 modifier: {modifier1} to row {current_row}")
                    try:
                        m1_selectors = [
                            f'table tbody tr:nth-child({current_row}) td:nth-child(8) input',  # M1 is 8th column
                            f'table tbody tr:nth-child({current_row}) input[data-fieldname*="MOD1"]',
                            f'table tbody tr:nth-child({current_row}) input[data-fieldname*="M1"]'
                        ]
                        
                        m1_added = False
                        for m1_selector in m1_selectors:
                            try:
                                m1_field = page.locator(m1_selector).first
                                if m1_field.is_visible() and m1_field.is_enabled():
                                    print(f"Found M1 field: {m1_selector}")
                                    
                                    # Highlight M1 field
                                    m1_field.evaluate("element => element.style.border = '3px solid blue'")
                                    page.wait_for_timeout(500)
                                    
                                    m1_field.click()
                                    m1_field.evaluate("element => element.value = ''")
                                    page.keyboard.type(modifier1, delay=100)
                                    
                                    # Remove highlight
                                    m1_field.evaluate("element => element.style.border = ''")
                                    
                                    print(f"Added M1: {modifier1} to row {current_row}")
                                    m1_added = True
                                    break
                            except Exception as e:
                                print(f"M1 selector {m1_selector} failed: {e}")
                                continue
                        
                        if not m1_added:
                            print(f"Could not add M1 to row {current_row}")
                            
                    except Exception as e:
                        print(f"Error adding M1: {e}")
                
                # Add M2 modifier if present
                if modifier2:
                    print(f"Adding M2 modifier: {modifier2} to row {current_row}")
                    try:
                        m2_selectors = [
                            f'table tbody tr:nth-child({current_row}) td:nth-child(9) input',  # M2 is 9th column
                            f'table tbody tr:nth-child({current_row}) input[data-fieldname*="MOD2"]',
                            f'table tbody tr:nth-child({current_row}) input[data-fieldname*="M2"]'
                        ]
                        
                        m2_added = False
                        for m2_selector in m2_selectors:
                            try:
                                m2_field = page.locator(m2_selector).first
                                if m2_field.is_visible() and m2_field.is_enabled():
                                    print(f"Found M2 field: {m2_selector}")
                                    
                                    # Highlight M2 field
                                    m2_field.evaluate("element => element.style.border = '3px solid orange'")
                                    page.wait_for_timeout(500)
                                    
                                    m2_field.click()
                                    m2_field.evaluate("element => element.value = ''")
                                    page.keyboard.type(modifier2, delay=100)
                                    
                                    # Remove highlight
                                    m2_field.evaluate("element => element.style.border = ''")
                                    
                                    print(f"Added M2: {modifier2} to row {current_row}")
                                    m2_added = True
                                    break
                            except Exception as e:
                                print(f"M2 selector {m2_selector} failed: {e}")
                                continue
                        
                        if not m2_added:
                            print(f"Could not add M2 to row {current_row}")
                            
                    except Exception as e:
                        print(f"Error adding M2: {e}")
                    
                print(f"Successfully added CPT code: {cpt_code} with modifiers to row {current_row}")
                
            except Exception as e:
                print(f"Error adding CPT code {i+1}: {e}")
                continue
            
            # Take screenshot after each CPT code
            page.screenshot(path=f"after_cpt_{i+1}_{cpt_code}.png")
            print(f"Screenshot: after_cpt_{i+1}_{cpt_code}.png")
            
            # Click safe area after processing each CPT code
            try:
                page.click('body', position={'x': 200, 'y': 200})
                page.wait_for_timeout(1000)
            except:
                pass
        
        print(f"\nCompleted adding {len(cpt_codes)-1} CPT codes")
        page.screenshot(path="final_cpt_result.png")
        
    except Exception as e:
        print(f"Error in CPT population: {e}")
        page.screenshot(path="cpt_error.png")

def add_icd_code(page, icd_code="A42.1"):
    """Add ICD code to ECW interface"""
    try:
        print(f"Adding ICD code {icd_code}...")
        page.wait_for_timeout(2000)
        
        icd_header = page.locator('h4:has-text("ICD Codes")').first
        if icd_header.is_visible():
            print("Found ICD Codes section")
            
            icd_code_selectors = [
                'input[ng-model="newICD"]',
                'input[class*="claimICDInput"]',
                'input[id*="txtnewIcd"]',
                'input[ng-keydown*="lookupICDCode"]'
            ]
            
            icd_field_found = False
            for selector in icd_code_selectors:
                try:
                    icd_field = page.locator(selector).first
                    if icd_field.is_visible():
                        print(f"Found ICD Code input field: {selector}")
                        icd_field.fill(icd_code)
                        print(f"Entered {icd_code} in ICD Code field")
                        
                        # Press Tab to populate other fields
                        print("Pressing Tab to populate ICD fields...")
                        page.keyboard.press('Tab')
                        page.wait_for_timeout(2000)
                        
                        print(f"Successfully added ICD code {icd_code}")
                        icd_field_found = True
                        break
                except:
                    continue
            
            if not icd_field_found:
                print("Could not find ICD Code input field under ICD Codes section")
        else:
            print("Could not find ICD Codes section")
            
    except Exception as e:
        print(f"Error adding ICD code: {e}")

def display_clinical_notes():
    """Display clinical notes from notes.txt"""
    try:
        notes_content = bedrock_cpt_predictor.read_text_file('notes.txt')
        print("=" * 50)
        print("CLINICAL NOTES FROM notes.txt:")
        print("=" * 50)
        print(notes_content[:1000] + ("..." if len(notes_content) > 1000 else ""))
        print("=" * 50)
    except Exception as e:
        print(f"Could not read notes.txt: {e}")

def populate_cpt_and_icd_codes(page, config):
    """Main function to populate CPT and ICD codes"""
    print("\n" + "=" * 60)
    print("STARTING CPT AND ICD CODE POPULATION")
    print("=" * 60)
    
    # Display clinical notes
    display_clinical_notes()
    
    # Get CPT code predictions from Bedrock
    predicted_cpt_codes = get_predicted_cpt_codes(config)
    
    # Add CPT codes starting from second code
    if predicted_cpt_codes and len(predicted_cpt_codes) > 1:
        print("\nUSING BEDROCK PREDICTED CPT CODES (starting from second code)")
        add_cpt_codes_to_ecw_interface(page, predicted_cpt_codes)
    elif predicted_cpt_codes and len(predicted_cpt_codes) == 1:
        print("\nONLY ONE CPT CODE FROM BEDROCK - no second code to add")
    else:
        print("\nNO CPT CODES FROM BEDROCK")
        print("Make sure you have:")
        print("1. notes.txt file with clinical notes")
        print("2. AWS credentials configured")
        print("3. Bedrock model access enabled")
    
    # Add ICD code
    add_icd_code(page, "A42.1")
    
    print("\n" + "=" * 60)
    print("CPT AND ICD CODE POPULATION COMPLETED")
    print("=" * 60)
    