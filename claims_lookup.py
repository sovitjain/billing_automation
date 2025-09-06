"""
Claims Lookup Module
Handles claim lookup operations based on claim ID in ECW
"""

def perform_claims_lookup(page, screenshot=True):
    """
    Perform initial claims lookup
    
    Args:
        page: Playwright page object
        screenshot: Whether to take screenshots
    
    Returns:
        bool: True if lookup successful, False otherwise
    """
    try:
        print("Looking for Lookup button...")
        
        lookup_selectors = [
            'text="Lookup"',
            'button:has-text("Lookup")',
            '#btnclaimlookup',
            '.btn:has-text("Lookup")',
            '[ng-click*="getClaimsListFromLookup"]'
        ]
        
        lookup_found = False
        for selector in lookup_selectors:
            try:
                lookup_button = page.locator(selector).first
                if lookup_button.is_visible():
                    print(f"Found Lookup button with selector: {selector}")
                    lookup_button.click()
                    page.wait_for_timeout(2000)
                    lookup_found = True
                    break
            except:
                continue
        
        if not lookup_found:
            print("Could not find Lookup button")
            return False
        
        print("Successfully clicked Lookup button")
        return True
        
    except Exception as e:
        print(f"Error in claims lookup: {e}")
        return False

def set_claim_status(page):
    """
    Set claim status to All Claims
    
    Args:
        page: Playwright page object
    
    Returns:
        bool: True if status set successfully, False otherwise
    """
    try:
        print("Setting Claim Status to All Claims...")
        page.wait_for_timeout(1000)
        claim_status_dropdown = page.locator('#claimStatusCodeId').first
        if claim_status_dropdown.is_visible():
            claim_status_dropdown.select_option(label="All Claims")
            print("Selected 'All Claims' from status dropdown")
            page.wait_for_timeout(1000)
            return True
        else:
            print("Could not find claim status dropdown")
            return False
    except Exception as e:
        print(f"Error setting claim status: {e}")
        return False

def select_patient_disabled(page, patient_name=""):
    """
    DISABLED: Patient selection function - no longer used for claim ID-based workflow
    """
    print("Patient selection has been disabled - searching by claim ID only")
    return False

def perform_main_lookup(page):
    """
    Perform main lookup to search for claims
    
    Args:
        page: Playwright page object
    
    Returns:
        bool: True if lookup successful, False otherwise
    """
    try:
        print("Looking for main Lookup button to perform search...")
        page.wait_for_timeout(1000)
        
        main_lookup_selectors = [
            '#btnclaimlookup',
            'button:has-text("Lookup")',
            '.btn:has-text("Lookup")',
            '[ng-click*="getClaimsListFromLookup"]'
        ]
        
        main_lookup_found = False
        for selector in main_lookup_selectors:
            try:
                main_lookup_button = page.locator(selector).first
                if main_lookup_button.is_visible():
                    print(f"Found main Lookup button with selector: {selector}")
                    main_lookup_button.click()
                    page.wait_for_timeout(3000)
                    print("Successfully clicked main Lookup button")
                    main_lookup_found = True
                    break
            except:
                continue
        
        if not main_lookup_found:
            print("Could not find main Lookup button")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error clicking main Lookup button: {e}")
        return False

def select_claim(page, claim_number="38939"):
    """
    Select specific claim from the results with enhanced searching
    
    Args:
        page: Playwright page object
        claim_number: Claim number to select
    
    Returns:
        bool: True if claim selected successfully, False otherwise
    """
    try:
        print(f"Looking for claim# {claim_number}...")
        page.wait_for_timeout(2000)
        
        
        # Try multiple ways to find the claim number
        claim_selectors = [
            f'text="{claim_number}"',
            f'a:has-text("{claim_number}")',
            f'td:has-text("{claim_number}")',
            f'[href*="{claim_number}"]',
            f'span:has-text("{claim_number}")',
            f'div:has-text("{claim_number}")',
            f'*:has-text("{claim_number}")',  # Any element containing the claim number
        ]
        
        claim_found = False
        for selector in claim_selectors:
            try:
                print(f"Trying selector: {selector}")
                claim_elements = page.locator(selector).all()
                
                if claim_elements:
                    print(f"Found {len(claim_elements)} elements with claim number {claim_number}")
                    
                    for i, element in enumerate(claim_elements):
                        try:
                            element_text = element.text_content()
                            print(f"Element {i}: '{element_text}'")
                            
                            # Check if this element contains exactly our claim number
                            if claim_number in element_text:
                                print(f"Clicking on claim element {i}: {element_text}")
                                element.click()
                                page.wait_for_timeout(3000)
                                print(f"Successfully clicked on claim# {claim_number}")
                                claim_found = True
                                break
                                
                        except Exception as element_error:
                            print(f"Error with element {i}: {element_error}")
                            continue
                    
                    if claim_found:
                        break
                        
            except Exception as selector_error:
                print(f"Selector {selector} failed: {selector_error}")
                continue
        
        if not claim_found:
            print(f"Direct search failed. Searching for partial matches...")
            
            # Try to find any element that contains digits and might be a claim
            try:
                # Look for any clickable elements containing numbers
                all_elements = page.locator('a, td, span, div').all()
                
                for i, element in enumerate(all_elements[:50]):  # Check first 50 elements
                    try:
                        text = element.text_content()
                        if text and text.strip().isdigit():
                            # Found a pure number
                            if claim_number in text or text in claim_number:
                                print(f"Found potential claim match: '{text}' - clicking...")
                                element.click()
                                page.wait_for_timeout(3000)
                                print(f"Successfully clicked on potential claim: {text}")
                                claim_found = True
                                break
                        elif text and claim_number in text:
                            # Found claim number within some text
                            print(f"Found claim number in text: '{text}' - clicking...")
                            element.click()
                            page.wait_for_timeout(3000)
                            print(f"Successfully clicked on claim containing: {claim_number}")
                            claim_found = True
                            break
                            
                    except:
                        continue
                        
            except Exception as search_error:
                print(f"Partial search failed: {search_error}")
        
        if not claim_found:
            print(f"Could not find claim# {claim_number} in search results")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error clicking claim# {claim_number}: {e}")
        return False

def complete_claims_lookup_workflow(page, claim_number="38939", patient_name="", screenshot=False):
    """
    Complete the entire claims lookup workflow - focus on claim number only
    
    Args:
        page: Playwright page object
        claim_number: Claim number to select
        patient_name: Not used (kept for compatibility)
        screenshot: Whether to take screenshots
    
    Returns:
        bool: True if entire workflow successful, False otherwise
    """
    try:
        # Step 1: Initial lookup
        if not perform_claims_lookup(page, screenshot):
            return False
        
        # Step 2: Set claim status
        if not set_claim_status(page):
            return False
        
        # Step 3: Perform main lookup (skip patient selection completely)
        if not perform_main_lookup(page):
            return False
        
        # Step 5: Look for claim number directly (this is the main goal)
        print(f"Searching for claim# {claim_number} in results...")
        if not select_claim(page, claim_number):
            print("Claim not found in search results")
            
            # List available claims for debugging
            print("Listing available claims...")
            try:
                # Look for claim numbers in the results
                claim_selectors = [
                    'td:has-text("#")',  # Cells that might contain claim numbers
                    'a[href*="claim"]',  # Links that might be claims
                    'td',  # All table cells
                    '.claim-number',  # Possible class names
                    '[data-claim]'  # Possible data attributes
                ]
                
                found_claims = []
                for selector in claim_selectors:
                    try:
                        elements = page.locator(selector).all()
                        for element in elements[:20]:  # Check first 20 elements
                            try:
                                text = element.text_content()
                                if text and text.strip().isdigit() and len(text.strip()) >= 4:
                                    found_claims.append(text.strip())
                            except:
                                continue
                    except:
                        continue
                
                if found_claims:
                    unique_claims = list(set(found_claims))[:10]  # Remove duplicates, show first 10
                    print("Available claim numbers found:")
                    for claim in unique_claims:
                        print(f"  - {claim}")
                    
                else:
                    print("No claim numbers found in current results")
                    
            except Exception as list_error:
                print(f"Error listing claims: {list_error}")
            
            return False
        
        print("Claims lookup workflow completed successfully")
        return True
        
    except Exception as e:
        print(f"Error in claims lookup workflow: {e}")
        return False