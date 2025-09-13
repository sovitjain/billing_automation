"""
ECW Navigation Module
Handles navigation within ECW system including calendar settings and menu navigation
"""

def setup_initial_navigation(page, config, screenshot=True):
    """
    Handle initial ECW navigation after login (S button, calendar, etc.)
    
    Args:
        page: Playwright page object
        config: Configuration object
        screenshot: Whether to take screenshots
    
    Returns:
        bool: True if navigation successful, False otherwise
    """
    try:
        target_date = config.get('DEFAULT', 'target_date')
        
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
        
        return True
        
    except Exception as e:
        print(f"Error in initial navigation: {e}")
        return False

def navigate_to_claims(page, screenshot=True):
    """
    Navigate to Billing > Claims
    
    Args:
        page: Playwright page object
        screenshot: Whether to take screenshots
    
    Returns:
        bool: True if navigation successful, False otherwise
    """
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
                    return True
                else:
                    print("Could not find Claims icon")
                    return False
            else:
                print("Could not find billing menu")
                return False
        else:
            print("Could not find hamburger menu")
            return False
            
    except Exception as e:
        print(f"Error navigating to Claims: {e}")
        return False

def set_service_dates(page, target_date, screenshot=False):
    """
    Set service dates in Claims page
    
    Args:
        page: Playwright page object
        target_date: Target date in MM-DD-YYYY format
        screenshot: Whether to take screenshots
    
    Returns:
        bool: True if dates set successfully, False otherwise
    """
    try:
        print(f"Setting Service Date range to: {target_date}")
        
        # Parse the target date properly - format is MM-DD-YYYY
        date_parts = target_date.split('-')
        target_month = int(date_parts[0])  # MM as integer
        target_day = int(date_parts[1])  # DD
        target_year = int(date_parts[2])  # YYYY
        
        # Month names for navigation
        month_names = ["January", "February", "March", "April", "May", "June", 
                     "July", "August", "September", "October", "November", "December"]
        target_month_name = month_names[target_month - 1]
        
        print(f"Service Date - Month: {target_month} ({target_month_name}), Day: {target_day}, Year: {target_year}")
        
        calendar_icons = page.locator('.icon.icon-inputcalender').all()
        
        if len(calendar_icons) >= 2:
            print("Found Service Date calendar icons...")
            
            # Function to set a specific date (FROM or TO)
            def set_calendar_date(calendar_icon, date_type):
                print(f"Setting {date_type} date...")
                calendar_icon.click()
                page.wait_for_timeout(2000)
                
                
                # Navigate to correct month using dropdown
                month_set = False
                try:
                    print(f"Looking for month dropdown to select {target_month_name}...")
                    
                    # Based on your screenshot, target the specific month dropdown structure
                    month_dropdown_selectors = [
                        'select.datepicker-months',  # Most common
                        'select[class*="month"]',
                        '.datepicker select:first-child',
                        'select:first-child',
                        'select',  # Any select element in the calendar
                        # Target the specific structure from your screenshot
                        '.datepicker-days select',
                        '.datepicker select',
                        '[class*="datepicker"] select'
                    ]
                    
                    for dropdown_selector in month_dropdown_selectors:
                        try:
                            month_dropdown = page.locator(dropdown_selector).first
                            if month_dropdown.is_visible():
                                print(f"Found month dropdown: {dropdown_selector}")
                                
                                
                                # Try different ways to select the target month
                                month_short_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                                                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                                month_options = [
                                    month_short_names[target_month - 1],  # Short name (Sep for September)
                                    target_month_name,  # Full name (September)
                                    str(target_month),    # Month as number (9)
                                    f"{target_month:02d}",   # Zero-padded month (09)
                                    str(target_month - 1),    # 0-indexed month (8 for September)
                                ]
                                
                                
                                for option in month_options:
                                    try:
                                        print(f"Attempting to select month option: '{option}'")
                                        
                                        # Try by visible text first
                                        month_dropdown.select_option(label=option)
                                        print(f"Successfully selected {target_month_name} using label: '{option}'")
                                        page.wait_for_timeout(1500)
                                        month_set = True
                                        break
                                        
                                    except Exception as label_error:
                                        try:
                                            # Try by value
                                            month_dropdown.select_option(value=option)
                                            print(f"Successfully selected {target_month_name} using value: '{option}'")
                                            page.wait_for_timeout(1500)
                                            month_set = True
                                            break
                                        except:
                                            continue
                                
                                if month_set:
                                    break
                                    
                        except:
                            continue
                    
                    # If dropdown method fails, try clicking on the month text directly
                    if not month_set:
                        print("Dropdown selection failed, trying to click month text directly...")
                        
                        # Try to click on "Sep" text to open month picker
                        month_text_selectors = [
                            '.datepicker-switch',
                            '.month',
                            '.current-month',
                            'th.datepicker-switch',
                            # Based on your screenshot structure
                            '.datepicker-days th.datepicker-switch'
                        ]
                        
                        for month_text_selector in month_text_selectors:
                            try:
                                month_text_element = page.locator(month_text_selector).first
                                if month_text_element.is_visible():
                                    month_text = month_text_element.text_content()
                                    print(f"Found month text element: '{month_text}' with selector: {month_text_selector}")
                                    
                                    # Click on it to potentially open month picker
                                    month_text_element.click()
                                    page.wait_for_timeout(1000)
                                    
                                    # Look for August in the opened month picker
                                    august_selectors = [
                                        'span:has-text("Aug")',
                                        'td:has-text("Aug")',
                                        'div:has-text("Aug")',
                                        '.month:has-text("Aug")',
                                        '*:has-text("Aug")'
                                    ]
                                    
                                    for aug_selector in august_selectors:
                                        try:
                                            aug_element = page.locator(aug_selector).first
                                            if aug_element.is_visible():
                                                print(f"Found August option: {aug_selector}")
                                                aug_element.click()
                                                page.wait_for_timeout(1000)
                                                month_set = True
                                                break
                                        except:
                                            continue
                                    
                                    if month_set:
                                        break
                                        
                            except:
                                continue
                
                except Exception as e:
                    print(f"Month navigation failed: {e}")
                
                # Last resort: use navigation arrows if nothing else worked
                if not month_set:
                    print("All month selection methods failed, trying navigation arrows...")
                    try:
                        # Look for current month display
                        current_month_selectors = [
                            '.datepicker-switch',
                            '.month',
                            '.current-month'
                        ]
                        
                        current_month_text = ""
                        for selector in current_month_selectors:
                            try:
                                element = page.locator(selector).first
                                if element.is_visible():
                                    current_month_text = element.text_content()
                                    break
                            except:
                                continue
                        
                        print(f"Current month showing: '{current_month_text}'")
                        
                        # If showing September and we want August, click previous
                        if "Sep" in current_month_text and target_month == 8:
                            prev_selectors = [
                                '.datepicker .prev',
                                'button.prev',
                                '.prev-month',
                                'th.prev',
                                '.datepicker-days .prev'
                            ]
                            
                            for prev_selector in prev_selectors:
                                try:
                                    prev_button = page.locator(prev_selector).first
                                    if prev_button.is_visible():
                                        print(f"Found previous month button: {prev_selector}")
                                        prev_button.click()
                                        page.wait_for_timeout(1000)
                                        print("Clicked previous month to go from September to August")
                                        month_set = True
                                        break
                                except:
                                    continue
                    except Exception as e:
                        print(f"Navigation arrow method failed: {e}")
                
                if not month_set:
                    print(f"WARNING: Could not set month to {target_month_name}, proceeding with current month")
                
                
                # Select the day
                print(f"Selecting day {target_day}...")
                day_selectors = [
                    f'td.day:has-text("{target_day}"):not(.old):not(.new):not(.today)',
                    f'table td:has-text("{target_day}"):not(:has-text("Today"))',
                    f'td[data-day="{target_day}"]',
                    f'button[data-day="{target_day}"]',
                    f'td:has-text("{target_day}"):not(button)',
                    f'div.calendar-day:has-text("{target_day}")'
                ]
                
                day_set = False
                for day_selector in day_selectors:
                    try:
                        day_elements = page.locator(day_selector).all()
                        
                        for day_element in day_elements:
                            element_text = day_element.text_content()
                            if element_text and element_text.strip() == str(target_day):
                                # Verify it's not a disabled/grayed out day
                                element_class = day_element.get_attribute('class') or ''
                                if 'old' not in element_class and 'new' not in element_class and 'disabled' not in element_class:
                                    print(f"Clicking {date_type} date day {target_day}")
                                    day_element.click()
                                    print(f"Set {date_type} date to: {target_month:02d}/{target_day:02d}/{target_year}")
                                    page.wait_for_timeout(1000)
                                    day_set = True
                                    break
                        
                        if day_set:
                            break
                            
                    except:
                        continue
                
                if not day_set:
                    print(f"Could not set {date_type} date to {target_day}")
                    return False
                
                return True
            
            # Set FROM date
            if not set_calendar_date(calendar_icons[0], "FROM"):
                print("Failed to set FROM date")
                return False
            
            # Set TO date
            if not set_calendar_date(calendar_icons[1], "TO"):
                print("Failed to set TO date")
                return False
            
            print("Successfully completed Service Date FROM and TO date setting")
            
            
            return True
            
        else:
            print(f"Found {len(calendar_icons)} calendar icons, expected at least 2")
            return False
            
    except Exception as e:
        print(f"Error setting dates in Claims page: {e}")
        return False