from playwright.sync_api import sync_playwright
import configparser
import os
import time
import json
import sys

# Import our CPT population module
try:
    import cpt_population
    print("Successfully imported cpt_population module")
except ImportError as e:
    print(f"Error importing cpt_population: {e}")
    print("Make sure cpt_population.py is in the same directory")
    sys.exit(1)

def load_config():
    config = configparser.ConfigParser()
    config.read('config.properties')
    return config

def format_notes(notes_text):
    """Format multi-line notes by replacing \\n with actual newlines"""
    if not notes_text:
        return ""
    # Replace literal \n with actual newlines
    formatted_notes = notes_text.replace('\\n', '\n')
    # Also handle other common escape sequences
    formatted_notes = formatted_notes.replace('\\t', '\t')
    return formatted_notes.strip()

def open_ecw_login():
    # Load configuration
    config = load_config()
    
    username = config.get('DEFAULT', 'username')
    password = config.get('DEFAULT', 'password')
    url = config.get('DEFAULT', 'url')
    provider_name = config.get('DEFAULT', 'provider_name')
    target_date = config.get('DEFAULT', 'target_date')
    headless = config.getboolean('BROWSER', 'headless')
    screenshot = config.getboolean('BROWSER', 'screenshot')
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=1000)
        page = browser.new_page()
        
        try:
            print("Opening ECW login page...")
            page.goto(url, wait_until='networkidle')
            
            print(f"Page title: {page.title()}")
            
            if screenshot:
                page.screenshot(path="ecw_login_before.png")
                print("Screenshot saved as ecw_login_before.png")
            
            page.wait_for_timeout(2000)
            
            # Username field selectors
            username_selectors = [
                'input[name="username"]',
                'input[name="userName"]',
                'input[name="user"]',
                'input[id="username"]',
                'input[id="userName"]',
                'input[id="user"]',
                'input[type="text"]',
                '#username',
                '#userName',
                '#user'
            ]
            
            # Password field selectors
            password_selectors = [
                'input[name="password"]',
                'input[name="pwd"]',
                'input[id="password"]',
                'input[id="pwd"]',
                'input[type="password"]',
                '#password',
                '#pwd'
            ]
            
            # Login button selectors
            login_button_selectors = [
                'input[type="submit"]',
                'button[type="submit"]',
                'input[value*="Login"]',
                'input[value*="Sign"]',
                'button:has-text("Login")',
                'button:has-text("Sign In")',
                '#login',
                '#loginButton',
                '.login-button',
                '.btn-login'
            ]
            
            # Find and fill username
            username_filled = False
            for selector in username_selectors:
                try:
                    if page.is_visible(selector):
                        print(f"Found username field with selector: {selector}")
                        page.fill(selector, username)
                        print(f"Filled username: {username}")
                        username_filled = True
                        break
                except:
                    continue
            
            if not username_filled:
                print("WARNING: Could not find username field!")
            
            # Try to fill password on the same page
            password_filled = False
            for selector in password_selectors:
                try:
                    if page.is_visible(selector):
                        print(f"Found password field with selector: {selector}")
                        page.fill(selector, password)
                        print("Filled password: ****")
                        password_filled = True
                        break
                except:
                    continue
            
            if not password_filled:
                print("Password field not found on current page - might be a two-step login")
            
            if screenshot:
                page.screenshot(path="ecw_login_filled.png")
                print("Screenshot saved as ecw_login_filled.png")
            
            # Find and click Next/Login button
            login_clicked = False
            for selector in login_button_selectors:
                try:
                    if page.is_visible(selector):
                        print(f"Found login button with selector: {selector}")
                        page.click(selector)
                        print("Clicked login button")
                        login_clicked = True
                        break
                except:
                    continue
            
            if not login_clicked:
                print("WARNING: Could not find login button!")
            
            # Wait for navigation after clicking Next/Login
            if login_clicked:
                try:
                    print("Waiting for page to load after clicking Next...")
                    page.wait_for_load_state('networkidle', timeout=10000)
                    print("Page loaded after Next button.")
                except:
                    print("Page might still be loading...")
            
            # Handle password page if needed
            if "getPwdPage" in page.url or not password_filled:
                print("Now on password page - looking for password field...")
                page.wait_for_timeout(2000)
                
                if screenshot:
                    page.screenshot(path="ecw_password_page.png")
                    print("Screenshot saved as ecw_password_page.png")
                
                # Fill password on password page
                password_filled_step2 = False
                for selector in password_selectors:
                    try:
                        if page.is_visible(selector):
                            print(f"Found password field on password page with selector: {selector}")
                            page.fill(selector, password)
                            print("Filled password: ****")
                            password_filled_step2 = True
                            break
                    except:
                        continue
                
                if not password_filled_step2:
                    print("WARNING: Could not find password field on password page!")
                
                if screenshot:
                    page.screenshot(path="ecw_password_filled.png")
                    print("Screenshot saved as ecw_password_filled.png")
                
                # Click login button on password page
                login_clicked_step2 = False
                for selector in login_button_selectors:
                    try:
                        if page.is_visible(selector):
                            print(f"Found login button on password page with selector: {selector}")
                            page.click(selector)
                            print("Clicked login button on password page")
                            login_clicked_step2 = True
                            break
                    except:
                        continue
                
                if not login_clicked_step2:
                    print("WARNING: Could not find login button on password page!")
                
                # Wait for final login
                if login_clicked_step2:
                    try:
                        print("Waiting for final login to complete...")
                        page.wait_for_load_state('networkidle', timeout=15000)
                        print("Final login completed!")
                    except:
                        print("Login might still be processing...")
            
            if screenshot:
                page.screenshot(path="ecw_login_after.png")
                print("Screenshot saved as ecw_login_after.png")
            
            print(f"Current URL: {page.url}")
            print(f"Current page title: {page.title()}")
            
            # After successful login
            if "login" not in page.url.lower():
                print("Login successful! Now navigating to claims...")
                page.wait_for_timeout(3000)
                
                if screenshot:
                    page.screenshot(path="ecw_dashboard.png")
                    print("Screenshot saved as ecw_dashboard.png")
                
                # Click "S" button
                try:
                    print("Looking for 'S' button...")
                    s_button = page.locator('text="S"').first
                    if s_button.is_visible():
                        print("Found 'S' button, clicking...")
                        s_button.click()
                        print("Clicked 'S' button")
                        page.wait_for_timeout(1000)
                    else:
                        print("Could not find 'S' button")
                except Exception as e:
                    print(f"Error clicking 'S' button: {e}")

                # Close submenus
                try:
                    print("Closing any open submenus...")
                    page.keyboard.press('Escape')
                    page.wait_for_timeout(1000)
                    page.click('body', position={'x': 400, 'y': 300})
                    page.wait_for_timeout(1000)
                    print("Submenus closed")
                except Exception as e:
                    print(f"Error closing submenus: {e}")

                # Change calendar date
                try:
                    print(f"Setting calendar date to: {target_date}")
                    target_month, target_day, target_year = target_date.split('-')
                    target_day = int(target_day)
                    
                    calendar_widget = page.locator('.icon.icon-inputcalender').first
                    
                    if calendar_widget.is_visible():
                        print("Found calendar widget, clicking...")
                        calendar_widget.click()
                        page.wait_for_timeout(2000)
                        
                        target_date_element = page.locator(f'text="{target_day}"').first
                        if target_date_element.is_visible():
                            print(f"Clicking on date {target_day}...")
                            target_date_element.click()
                            page.wait_for_timeout(1000)
                            print(f"Successfully selected date {target_day}")
                        else:
                            print(f"Could not find date {target_day} in calendar")
                    else:
                        print("Could not find calendar widget")
                        
                except Exception as e:
                    print(f"Error setting calendar date: {e}")

                # Navigate to Billing > Claims
                try:
                    print("Navigating to Billing via hamburger menu...")
                    
                    # Click hamburger menu
                    hamburger = page.locator('#jellybean-panelLink4.navgator.mainMenu').first
                    if hamburger.is_visible():
                        print("Found hamburger menu, clicking...")
                        hamburger.click()
                        page.wait_for_timeout(2000)
                        
                        # Click Billing
                        billing_menu = page.locator('.icon.nav-label.icon-label-bill').first
                        if billing_menu.is_visible():
                            print("Found billing menu, clicking...")
                            billing_menu.click()
                            page.wait_for_timeout(2000)
                            
                            # Click Claims
                            claims_icon = page.locator('.svgicon.svg-document1').first
                            if claims_icon.is_visible():
                                print("Found Claims icon, clicking...")
                                claims_icon.click()
                                page.wait_for_timeout(3000)
                                print("Successfully navigated to Claims")
                                
                                # Set service dates
                                try:
                                    print(f"Setting Service Date range to: {target_date}")
                                    
                                    calendar_icons = page.locator('.icon.icon-inputcalender').all()
                                    
                                    if len(calendar_icons) >= 2:
                                        print("Found Service Date calendar icons...")
                                        
                                        # Set FROM date
                                        print("Setting FROM date...")
                                        calendar_icons[0].click()
                                        page.wait_for_timeout(1000)
                                        
                                        target_day = int(target_date.split('-')[1])
                                        from_date_element = page.locator(f'text="{target_day}"').first
                                        if from_date_element.is_visible():
                                            from_date_element.click()
                                            print(f"Set FROM date to: {target_day}")
                                            page.wait_for_timeout(1000)
                                        
                                        # Set TO date
                                        print("Setting TO date...")
                                        calendar_icons[1].click()
                                        page.wait_for_timeout(1000)
                                        
                                        to_date_element = page.locator(f'text="{target_day}"').first
                                        if to_date_element.is_visible():
                                            to_date_element.click()
                                            print(f"Set TO date to: {target_day}")
                                            page.wait_for_timeout(1000)
                                        
                                        print("Successfully set both Service Date FROM and TO dates")
                                        
                                        # Click initial Lookup button
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
                                            
                                            if lookup_found:
                                                print("Successfully clicked Lookup button")
                                                
                                                # Set Claim Status to All Claims
                                                try:
                                                    print("Setting Claim Status to All Claims...")
                                                    page.wait_for_timeout(1000)
                                                    claim_status_dropdown = page.locator('#claimStatusCodeId').first
                                                    if claim_status_dropdown.is_visible():
                                                        claim_status_dropdown.select_option(label="All Claims")
                                                        print("Selected 'All Claims' from status dropdown")
                                                        page.wait_for_timeout(1000)
                                                    else:
                                                        print("Could not find claim status dropdown")
                                                except Exception as e:
                                                    print(f"Error setting claim status: {e}")
                                                
                                                # Select patient Test, Manu
                                                try:
                                                    print("Looking for patient Test, Manu...")
                                                    page.wait_for_timeout(1000)
                                                    
                                                    patient_selectors = [
                                                        'h4:has-text("Test, Manu")',
                                                        'text="Test, Manu"',
                                                        '[ng-click*="selectPatient"]:has-text("Test, Manu")',
                                                        '.nameTextInlineWidth:has-text("Test, Manu")'
                                                    ]
                                                    
                                                    patient_found = False
                                                    for selector in patient_selectors:
                                                        try:
                                                            patient_option = page.locator(selector).first
                                                            if patient_option.is_visible():
                                                                print(f"Found Test, Manu patient with selector: {selector}")
                                                                patient_option.click()
                                                                page.wait_for_timeout(2000)
                                                                print("Selected Test, Manu patient")
                                                                patient_found = True
                                                                break
                                                        except:
                                                            continue
                                                    
                                                    if not patient_found:
                                                        print("Could not find Test, Manu patient")
                                                        
                                                except Exception as e:
                                                    print(f"Error selecting patient: {e}")
                                                
                                                # Click main Lookup button to search
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
                                                        
                                                except Exception as e:
                                                    print(f"Error clicking main Lookup button: {e}")
                                                
                                                # Click on claim# 38000
                                                try:
                                                    print("Looking for claim# 38000...")
                                                    page.wait_for_timeout(2000)
                                                    
                                                    claim_selectors = [
                                                        'text="38000"',
                                                        'a:has-text("38000")',
                                                        'td:has-text("38000")',
                                                        '[href*="38000"]'
                                                    ]
                                                    
                                                    claim_found = False
                                                    for selector in claim_selectors:
                                                        try:
                                                            claim_element = page.locator(selector).first
                                                            if claim_element.is_visible():
                                                                print(f"Found claim# 38000 with selector: {selector}")
                                                                claim_element.click()
                                                                page.wait_for_timeout(3000)
                                                                print("Successfully clicked on claim# 38000")
                                                                claim_found = True
                                                                break
                                                        except:
                                                            continue
                                                    
                                                    if not claim_found:
                                                        print("Could not find claim# 38000")
                                                        
                                                except Exception as e:
                                                    print(f"Error clicking claim# 38000: {e}")
                                                
                                                # ==================================================
                                                # CALL CPT POPULATION MODULE FROM HERE
                                                # ==================================================
                                                print("\n" + "=" * 60)
                                                print("HANDING OFF TO CPT POPULATION MODULE")
                                                print("=" * 60)
                                                
                                                # Call the CPT population function from the separate module
                                                cpt_population.populate_cpt_and_icd_codes(page, config)
                                                
                                            else:
                                                print("Could not find Lookup button")
                                                
                                        except Exception as e:
                                            print(f"Error in lookup process: {e}")
                                            
                                    else:
                                        print(f"Found {len(calendar_icons)} calendar icons, expected at least 2")
                                
                                except Exception as e:
                                    print(f"Error setting dates in Claims page: {e}")
                                
                            else:
                                print("Could not find Claims icon")
                        else:
                            print("Could not find billing menu")
                    else:
                        print("Could not find hamburger menu")
                
                except Exception as e:
                    print(f"Error navigating to Claims: {e}")

                # Take final screenshot
                page.wait_for_timeout(2000)
                if screenshot:
                    page.screenshot(path="ecw_final_state.png")
                    print("Screenshot saved as ecw_final_state.png")
            
            else:
                print("Still on login page - login may have failed")
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            page.screenshot(path="ecw_login_error.png")
        
        # Keep browser open for interaction
        print("\nBrowser will stay open. Press Enter to close...")
        input()
        
        browser.close()

if __name__ == "__main__":
    if not os.path.exists('config.properties'):
        print("Error: config.properties file not found!")
        print("Please create the file and add your credentials.")
    else:
        open_ecw_login()