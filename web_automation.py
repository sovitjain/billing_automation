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
    claim_number = config.get('DEFAULT', 'claim_number', fallback='38939')
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
                print("Claims lookup failed. Exiting...")
                return 1
            
            # Step 6: Extract Progress Notes
            print("\n" + "=" * 60)
            print("STEP 6: EXTRACT PROGRESS NOTES")
            print("=" * 60)
            
            clinical_notes = extract_progress_notes(page, screenshot)
            
            if not clinical_notes or len(clinical_notes.strip()) < 50:
                print("Progress Notes extraction failed or returned insufficient content")
                clinical_notes = "No clinical notes extracted - using fallback"
            
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