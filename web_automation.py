from playwright.sync_api import sync_playwright
import configparser
import os
import time

def load_config():
    config = configparser.ConfigParser()
    config.read('config.properties')
    return config

def open_ecw_login():
    # Load configuration
    config = load_config()
    
    username = config.get('DEFAULT', 'username')
    password = config.get('DEFAULT', 'password')  # Already reading password from config
    url = config.get('DEFAULT', 'url')
    provider_name = config.get('DEFAULT', 'provider_name')
    target_date = config.get('DEFAULT', 'target_date')
    headless = config.getboolean('BROWSER', 'headless')
    screenshot = config.getboolean('BROWSER', 'screenshot')
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=headless, slow_mo=1000)  # slow_mo adds delay between actions
        page = browser.new_page()
        
        try:
            # Navigate to login page
            print("Opening ECW login page...")
            page.goto(url, wait_until='networkidle')  # Fixed: use url variable instead of config.URL
            
            print(f"Page title: {page.title()}")
            
            # Take initial screenshot
            if screenshot:
                page.screenshot(path="ecw_login_before.png")
                print("Screenshot saved as ecw_login_before.png")
            
            # Wait a moment for page to fully load
            page.wait_for_timeout(2000)
            
            # Try common username field selectors
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
            
            # Try common password field selectors
            password_selectors = [
                'input[name="password"]',
                'input[name="pwd"]',
                'input[id="password"]',
                'input[id="pwd"]',
                'input[type="password"]',
                '#password',
                '#pwd'
            ]
            
            # Try common login button selectors
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
                print("Available input fields:")
                inputs = page.query_selector_all('input')
                for i, input_elem in enumerate(inputs):
                    input_type = input_elem.get_attribute('type') or 'text'
                    input_name = input_elem.get_attribute('name') or 'no name'
                    input_id = input_elem.get_attribute('id') or 'no id'
                    print(f"  Input {i+1}: type='{input_type}', name='{input_name}', id='{input_id}'")
            
            # Step 1: Try to fill password on the same page (in case it's a single-step login)
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
            
            # Take screenshot after filling fields
            if screenshot:
                page.screenshot(path="ecw_login_filled.png")
                print("Screenshot saved as ecw_login_filled.png")
            
            # Find and click Next/Login button (for username step)
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
                print("Available buttons and submit inputs:")
                buttons = page.query_selector_all('button, input[type="submit"]')
                for i, button in enumerate(buttons):
                    button_text = button.text_content() or button.get_attribute('value') or 'no text'
                    button_type = button.get_attribute('type') or 'button'
                    print(f"  Button {i+1}: type='{button_type}', text='{button_text}'")
            
            # Wait for navigation after clicking Next/Login
            if login_clicked:
                try:
                    print("Waiting for page to load after clicking Next...")
                    page.wait_for_load_state('networkidle', timeout=10000)
                    print("Page loaded after Next button.")
                except:
                    print("Page might still be loading...")
            
            # Step 2: Check if we're now on password page and handle it
            if "getPwdPage" in page.url or not password_filled:
                print("Now on password page - looking for password field...")
                
                # Wait a moment for the password page to fully load
                page.wait_for_timeout(2000)
                
                # Take screenshot of password page
                if screenshot:
                    page.screenshot(path="ecw_password_page.png")
                    print("Screenshot saved as ecw_password_page.png")
                
                # Try to find and fill password field on the new page
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
                    print("Available input fields on password page:")
                    inputs = page.query_selector_all('input')
                    for i, input_elem in enumerate(inputs):
                        input_type = input_elem.get_attribute('type') or 'text'
                        input_name = input_elem.get_attribute('name') or 'no name'
                        input_id = input_elem.get_attribute('id') or 'no id'
                        print(f"  Input {i+1}: type='{input_type}', name='{input_name}', id='{input_id}'")
                
                # Take screenshot after filling password
                if screenshot:
                    page.screenshot(path="ecw_password_filled.png")
                    print("Screenshot saved as ecw_password_filled.png")
                
                # Find and click login button on password page
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
                    print("Available buttons on password page:")
                    buttons = page.query_selector_all('button, input[type="submit"]')
                    for i, button in enumerate(buttons):
                        button_text = button.text_content() or button.get_attribute('value') or 'no text'
                        button_type = button.get_attribute('type') or 'button'
                        print(f"  Button {i+1}: type='{button_type}', text='{button_text}'")
                
                # Wait for final login
                if login_clicked_step2:
                    try:
                        print("Waiting for final login to complete...")
                        page.wait_for_load_state('networkidle', timeout=15000)
                        print("Final login completed!")
                    except:
                        print("Login might still be processing...")
            
            # Take final screenshot
            if screenshot:
                page.screenshot(path="ecw_login_after.png")
                print("Screenshot saved as ecw_login_after.png")
            
            print(f"Current URL: {page.url}")
            print(f"Current page title: {page.title()}")
            
            # After successful login, click "S" button and change date
            if "login" not in page.url.lower():
                print("Login successful! Now clicking 'S' button and changing date...")
                
                # Wait for the main dashboard to load
                page.wait_for_timeout(3000)
                
                # Take screenshot of dashboard
                if screenshot:
                    page.screenshot(path="ecw_dashboard.png")
                    print("Screenshot saved as ecw_dashboard.png")
                
                # Click on the "S" button in top right
                try:
                    print("Looking for 'S' button in top right...")
                    
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
                
                # Close any open submenus first
                try:
                    print("Checking for open submenus and closing them...")
                    
                    # Press Escape key to close any open menus/dropdowns
                    page.keyboard.press('Escape')
                    page.wait_for_timeout(1000)
                    
                    # Click somewhere neutral on the page to close menus
                    page.click('body', position={'x': 400, 'y': 300})
                    page.wait_for_timeout(1000)
                    
                    # Look for any visible overlay or dropdown menus and close them
                    menu_close_selectors = [
                        '.dropdown-menu.show',
                        '.open .dropdown-menu',
                        '.submenu',
                        '[aria-expanded="true"]'
                    ]
                    
                    for selector in menu_close_selectors:
                        try:
                            menu = page.locator(selector).first
                            if menu.is_visible():
                                print(f"Found open menu: {selector}")
                                # Try clicking outside the menu
                                page.click('body', position={'x': 100, 'y': 100})
                                page.wait_for_timeout(500)
                        except:
                            continue
                    
                    print("Submenus closed, proceeding with date navigation...")
                    
                except Exception as e:
                    print(f"Error closing submenus: {e}")

                # Click on the calendar widget to change the date
                try:
                    print(f"Looking for calendar widget to set date to: {target_date}")
                    
                    # Parse target date
                    target_month, target_day, target_year = target_date.split('-')
                    target_day = int(target_day)
                    
                    print(f"Target day: {target_day}")
                    
                    date_changed = False
                    
                    # Look for calendar widget with specific class
                    print("Looking for calendar widget with class 'icon icon-inputcalender'...")
                    
                    calendar_widget = page.locator('.icon.icon-inputcalender').first
                    
                    if calendar_widget.is_visible():
                        print("✅ Found calendar widget, clicking to open...")
                        calendar_widget.click()
                        page.wait_for_timeout(2000)  # Wait for calendar to open
                        
                        # Look for the target date in the calendar
                        print(f"Looking for date {target_day} in the calendar...")
                        
                        target_date_element = page.locator(f'text="{target_day}"').first
                        
                        if target_date_element.is_visible():
                            print(f"✅ Clicking on date {target_day} in calendar...")
                            target_date_element.click()
                            page.wait_for_timeout(1000)
                            print(f"Successfully selected date {target_day}")
                            date_changed = True
                        else:
                            print(f"❌ Could not find date {target_day} in the calendar")
                    
                    else:
                        print("❌ Could not find calendar widget with class 'icon icon-inputcalender'")
                    
                    if not date_changed:
                        print(f"WARNING: Could not change date to {target_date}")
                
                except Exception as e:
                    print(f"Error during calendar widget interaction: {e}")
                
                # Navigate to Billing via hamburger menu
                try:
                    print("Navigating to Billing via hamburger menu...")
                    
                    # Click hamburger menu using specific ID and class
                    hamburger = page.locator('#jellybean-panelLink4.navgator.mainMenu').first
                    if hamburger.is_visible():
                        print("Found hamburger menu, clicking...")
                        hamburger.click()
                        page.wait_for_timeout(2000)
                        
                        # Click Billing using specific class
                        billing_menu = page.locator('.icon.nav-label.icon-label-bill').first
                        if billing_menu.is_visible():
                            print("Found billing menu, clicking...")
                            billing_menu.click()
                            page.wait_for_timeout(2000)
                            
                            # Click Claims using SVG icon class
                            claims_icon = page.locator('.svgicon.svg-document1').first
                            if claims_icon.is_visible():
                                print("Found Claims icon, clicking...")
                                claims_icon.click()
                                page.wait_for_timeout(3000)
                                print("Successfully navigated to Claims")
                                
                                # Set dates in Claims page
                                try:
                                    print(f"Setting Service Date range to: {target_date}")
                                    
                                    # Find calendar icons for Service Date
                                    calendar_icons = page.locator('.icon.icon-inputcalender').all()
                                    
                                    if len(calendar_icons) >= 2:
                                        print("Found Service Date calendar icons...")
                                        
                                        # Set FROM date (first calendar icon)
                                        print("Setting FROM date...")
                                        calendar_icons[0].click()
                                        page.wait_for_timeout(1000)
                                        
                                        target_day = int(target_date.split('-')[1])
                                        from_date_element = page.locator(f'text="{target_day}"').first
                                        if from_date_element.is_visible():
                                            from_date_element.click()
                                            print(f"Set FROM date to: {target_day}")
                                            page.wait_for_timeout(1000)
                                        
                                        # Set TO date (second calendar icon)
                                        print("Setting TO date...")
                                        calendar_icons[1].click()
                                        page.wait_for_timeout(1000)
                                        
                                        to_date_element = page.locator(f'text="{target_day}"').first
                                        if to_date_element.is_visible():
                                            to_date_element.click()
                                            print(f"Set TO date to: {target_day}")
                                            page.wait_for_timeout(1000)
                                        
                                        print("Successfully set both Service Date FROM and TO dates")
                                        
                                        # Look for various Lookup button selectors
                                        try:
                                            print("Looking for Lookup button with multiple selectors...")
                                            
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
                                                
                                                # Click on claim# 38000 for Test, Manu
                                                try:
                                                    print("Looking for claim# 38000 for Test, Manu...")
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
                                                
                                                # Add CPT code 99213 directly without clicking Add
                                                try:
                                                    print("Adding CPT code 99213 directly...")
                                                    page.wait_for_timeout(2000)
                                                    
                                                    # Enter CPT code 99213 directly in the Code field (skip Add button)
                                                    code_field = page.locator('#billingClaimIpt34').first
                                                    if code_field.is_visible():
                                                        print("Found Code field, entering 99213...")
                                                        code_field.fill("99213")
                                                        print("Entered 99213 in Code field")
                                                        print("DEBUG: Current page URL after entering 99213:", page.url)
                                                        print("DEBUG: Current page title after entering 99213:", page.title())
                                                        
                                                        # Wait a moment before Tab
                                                        print("DEBUG: Waiting 1 second before pressing Tab...")
                                                        page.wait_for_timeout(1000)
                                                        
                                                        # Press Tab to populate other fields
                                                        print("DEBUG: About to press Tab key...")
                                                        page.keyboard.press('Tab')
                                                        print("DEBUG: Tab key pressed")
                                                        
                                                        # Check what happened after Tab
                                                        page.wait_for_timeout(2000)
                                                        print("DEBUG: Current page URL after Tab:", page.url)
                                                        print("DEBUG: Current page title after Tab:", page.title())
                                                        
                                                        # Check if we're still on claims page or if lookup opened
                                                        if "assessment" in page.url.lower() or "Select Assessments" in page.title():
                                                            print("DEBUG: ❌ Assessment lookup page opened! This is the problem.")
                                                            print("DEBUG: Trying to close this page and return to claims...")
                                                            
                                                            # Try to close this popup/page
                                                            try:
                                                                # Look for close button or press Escape
                                                                close_selectors = [
                                                                    'button:has-text("Close")',
                                                                    'button:has-text("Cancel")',
                                                                    '.close',
                                                                    '[aria-label="Close"]'
                                                                ]
                                                                
                                                                closed = False
                                                                for selector in close_selectors:
                                                                    try:
                                                                        close_btn = page.locator(selector).first
                                                                        if close_btn.is_visible():
                                                                            print(f"DEBUG: Found close button: {selector}")
                                                                            close_btn.click()
                                                                            closed = True
                                                                            break
                                                                    except:
                                                                        continue
                                                                
                                                                if not closed:
                                                                    print("DEBUG: Trying Escape key to close...")
                                                                    page.keyboard.press('Escape')
                                                                
                                                                page.wait_for_timeout(1000)
                                                                print("DEBUG: Attempted to close assessment page")
                                                                
                                                            except Exception as e:
                                                                print(f"DEBUG: Error closing assessment page: {e}")
                                                        else:
                                                            print("DEBUG: ✅ Still on correct page, CPT auto-population should work")
                                                        
                                                        print("Successfully added CPT code 99213")
                                                    else:
                                                        print("Could not find Code field")
                                                        
                                                except Exception as e:
                                                    print(f"Error adding CPT code: {e}")
                                                
                                                # Add ICD code A42.1 in the ICD Codes section
                                                try:
                                                    print("Adding ICD code A42.1 in ICD Codes section...")
                                                    page.wait_for_timeout(2000)
                                                    
                                                    # Find the ICD Codes header section
                                                    icd_header = page.locator('h4:has-text("ICD Codes")').first
                                                    if icd_header.is_visible():
                                                        print("Found ICD Codes header section")
                                                        
                                                        # Look for the Code column input field under ICD Codes section
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
                                                                    print(f"Found ICD Code input field with selector: {selector}")
                                                                    icd_field.fill("A42.1")
                                                                    print("Entered A42.1 in ICD Code field")
                                                                    
                                                                    # Press Tab to populate other fields
                                                                    print("Pressing Tab to populate ICD fields...")
                                                                    page.keyboard.press('Tab')
                                                                    page.wait_for_timeout(2000)
                                                                    
                                                                    print("Successfully added ICD code A42.1")
                                                                    icd_field_found = True
                                                                    break
                                                            except:
                                                                continue
                                                        
                                                        if not icd_field_found:
                                                            print("Could not find ICD Code input field under ICD Codes section")
                                                    else:
                                                        print("Could not find ICD Codes header section")
                                                        
                                                except Exception as e:
                                                    print(f"Error adding ICD code: {e}")
                                                
                                            else:
                                                print("Could not find any Lookup button")
                                                
                                        except Exception as e:
                                            print(f"Error in lookup process: {e}")
                                            
                                    else:
                                        print(f"Found {len(calendar_icons)} calendar icons, expected at least 2")
                                
                                except Exception as e:
                                    print(f"Error setting dates in Claims page: {e}")
                                
                            else:
                                print("Could not find Claims icon with class svgicon svg-document1")
                        else:
                            print("Could not find billing menu")
                    else:
                        print("Could not find hamburger menu")
                
                except Exception as e:
                    print(f"Error navigating to Claims: {e}")

                # Take final screenshot after changes
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