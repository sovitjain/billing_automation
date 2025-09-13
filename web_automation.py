#!/usr/bin/env python3
"""
Main ECW Web Automation Script - Modular Version
Orchestrates the complete ECW automation workflow using separate modules
"""

from playwright.sync_api import sync_playwright
import configparser
import os
import sys

# Import our modules
try:
    from ecw_login import handle_ecw_login
    from ecw_navigation import setup_initial_navigation, navigate_to_claims, set_service_dates
    from claims_lookup import complete_claims_lookup_workflow
    from progress_notes_extractor import extract_progress_notes
    from cpt_population import populate_cpt_and_icd_codes
    print("Successfully imported all modules")
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all module files are in the same directory:")
    print("- ecw_login.py")
    print("- ecw_navigation.py") 
    print("- claims_lookup.py")
    print("- progress_notes_extractor.py")
    print("- cpt_population.py")
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
    print("🔍 DEBUG: ANORECTAL MANOMETRY STATUS CHECK")
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
    
    print(f"📋 Clinical Notes Length: {len(clinical_notes)} characters")
    print(f"🔍 Searching for manometry status indicators...")
    print()
    
    # Show the result
    if deferred_found and not performed_found:
        print("🚫 RESULT: Anorectal manometry was DEFERRED/NOT DONE")
        print(f"   Found keyword: '{deferred_match}'")
        print("   ❌ CPT Code 91122 should be REMOVED")
        print("   Reason: Manometry was not performed")
    elif performed_found and not deferred_found:
        print("✅ RESULT: Anorectal manometry was PERFORMED")
        print(f"   Found keyword: '{performed_match}'")
        print("   ✅ CPT Code 91122 should be KEPT")
        print("   Reason: Manometry was successfully performed")
    elif deferred_found and performed_found:
        print("⚠️  RESULT: CONFLICTING INFORMATION FOUND")
        print(f"   Deferred keyword: '{deferred_match}'")
        print(f"   Performed keyword: '{performed_match}'")
        print("   🤔 MANUAL REVIEW REQUIRED")
        print("   Recommendation: Check clinical notes manually")
    else:
        print("❓ RESULT: NO CLEAR MANOMETRY STATUS FOUND")
        print("   No specific keywords found for performed/deferred status")
        print("   🤔 MANUAL REVIEW REQUIRED")
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
            print("📝 RELEVANT SNIPPET FROM CLINICAL NOTES:")
            print("-" * 40)
            print(f"...{snippet}...")
            print("-" * 40)
            print()

def main():
    """Main automation workflow"""
    print("=" * 80)
    print("ECW WEB AUTOMATION - MODULAR VERSION")
    print("=" * 80)
    
    # Check if config file exists
    if not os.path.exists('config.properties'):
        print("Error: config.properties file not found!")
        print("Please create the file and add your credentials.")
        return 1
    
    # Load configuration
    config = load_config()
    
    # Get configuration values
    headless = config.getboolean('BROWSER', 'headless', fallback=False)
    screenshot = config.getboolean('BROWSER', 'screenshot', fallback=True)
    target_date = config.get('DEFAULT', 'target_date')
    claim_number = config.get('CLAIMS', 'claim_id', fallback='38939')
    patient_name = config.get('DEFAULT', 'patient_name', fallback='')
    
    print(f"Configuration loaded:")
    print(f"  - Headless mode: {headless}")
    print(f"  - Screenshots: {screenshot}")
    print(f"  - Target date: {target_date}")
    print(f"  - Claim number: {claim_number}")
    print(f"  - Claim number: {claim_number} (patient selection disabled)")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=1000)
        page = browser.new_page()
        
        try:
            # Step 1: ECW Login
            print("\n" + "=" * 60)
            print("STEP 1: ECW LOGIN")
            print("=" * 60)
            
            if not handle_ecw_login(page, config, screenshot):
                print("Login failed. Exiting...")
                return 1
            
            print("Login successful! Proceeding to navigation...")
            page.wait_for_timeout(3000)
            
            # Step 2: Initial Navigation Setup
            # print("\n" + "=" * 60)
            # print("STEP 2: INITIAL NAVIGATION SETUP")
            # print("=" * 60)
            
            # if not setup_initial_navigation(page, config, screenshot):
            #     print("Initial navigation failed. Exiting...")
            #     return 1
            
            # Step 3: Navigate to Claims
            print("\n" + "=" * 60)
            print("STEP 3: NAVIGATE TO CLAIMS")
            print("=" * 60)
            
            if not navigate_to_claims(page, screenshot):
                print("Navigation to Claims failed. Exiting...")
                return 1
            
            # Step 4: Set Service Dates
            print("\n" + "=" * 60)
            print("STEP 4: SET SERVICE DATES")
            print("=" * 60)
            
            if not set_service_dates(page, target_date, screenshot):
                print("Setting service dates failed. Continuing anyway...")
            
            # Step 5: Claims Lookup Workflow
            print("\n" + "=" * 60)
            print("STEP 5: CLAIMS LOOKUP WORKFLOW")
            print("=" * 60)
            
            if not complete_claims_lookup_workflow(page, claim_number, "", screenshot):
                print("Claims lookup failed. Continuing with next steps...")
                # Continue execution instead of exiting
            
            # Step 6: Extract Progress Notes with retry logic
            print("\n" + "=" * 60)
            print("STEP 6: EXTRACT PROGRESS NOTES")
            print("=" * 60)
            
            clinical_notes = None
            max_retries = 3
            
            for attempt in range(max_retries):
                print(f"Progress Notes extraction attempt {attempt + 1}/{max_retries}")
                
                try:
                    clinical_notes = extract_progress_notes(page, screenshot)
                    
                    if clinical_notes and len(clinical_notes.strip()) >= 50:
                        print(f"SUCCESS: Progress Notes extracted successfully ({len(clinical_notes)} characters)")
                        break
                    else:
                        print(f"ATTEMPT {attempt + 1}: Extracted notes too short or empty")
                        if attempt < max_retries - 1:
                            print("Retrying progress notes extraction...")
                            page.wait_for_timeout(2000)  # Wait 2 seconds before retry
                except Exception as e:
                    print(f"ATTEMPT {attempt + 1}: Error during extraction - {e}")
                    if attempt < max_retries - 1:
                        print("Retrying progress notes extraction...")
                        page.wait_for_timeout(2000)
            
            if not clinical_notes or len(clinical_notes.strip()) < 50:
                print("=" * 60)
                print("CRITICAL: Progress Notes extraction FAILED after 3 attempts")
                print("MANUAL INTERVENTION REQUIRED")
                print("Please manually extract progress notes or check the web page.")
                print("=" * 60)
                
                # Wait for human input instead of proceeding
                user_input = input("Enter 'c' to continue with empty notes, or 'q' to quit: ").lower()
                if user_input == 'q':
                    print("Automation stopped by user request.")
                    return 1
                else:
                    clinical_notes = "No clinical notes extracted - manual intervention required"
            else:
                # Debug: Check anorectal manometry status in extracted clinical notes
                print("\n" + "=" * 60)
                print("STEP 6.5: ANORECTAL MANOMETRY STATUS DEBUG CHECK")
                print("=" * 60)
                debug_manometry_status(clinical_notes)
            
            # Step 7: Populate CPT and ICD Codes
            print("\n" + "=" * 60)
            print("STEP 7: POPULATE CPT AND ICD CODES")
            print("=" * 60)
            
            try:
                populate_cpt_and_icd_codes(page, clinical_notes)
            except Exception as cpt_error:
                print(f"Error in CPT population: {cpt_error}")
                print("Continuing to final steps...")
            
            # Step 8: Final Steps
            print("\n" + "=" * 60)
            print("STEP 8: FINAL STEPS")
            print("=" * 60)
            
            # Take final screenshot
            page.wait_for_timeout(2000)
            if screenshot:
                page.screenshot(path="ecw_final_state.png")
                print("Screenshot saved as ecw_final_state.png")
            
            print("\n" + "=" * 80)
            print("ECW AUTOMATION COMPLETED SUCCESSFULLY")
            print("=" * 80)
            
            # Keep browser open for interaction
            print("\nBrowser will stay open. Press Enter to close...")
            input()
            
        except Exception as e:
            print(f"\nAn error occurred during automation: {str(e)}")
            if screenshot:
                page.screenshot(path="automation_error.png")
                print("Error screenshot saved as automation_error.png")
            return 1
        
        finally:
            browser.close()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)