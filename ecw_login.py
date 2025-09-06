"""
ECW Login Module
Handles ECW login process including two-step authentication
"""

def handle_ecw_login(page, config, screenshot=False):
    """
    Handle ECW login process
    
    Args:
        page: Playwright page object
        config: Configuration object with credentials
        screenshot: Whether to take screenshots
    
    Returns:
        bool: True if login successful, False otherwise
    """
    try:
        username = config.get('DEFAULT', 'username')
        password = config.get('DEFAULT', 'password')
        url = config.get('DEFAULT', 'url')
        
        print("Opening ECW login page...")
        page.goto(url, wait_until='networkidle')
        
        print(f"Page title: {page.title()}")
        
        
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
            return False
        
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
            return False
        
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
                return False
            
            
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
                return False
            
            # Wait for final login
            if login_clicked_step2:
                try:
                    print("Waiting for final login to complete...")
                    page.wait_for_load_state('networkidle', timeout=15000)
                    print("Final login completed!")
                except:
                    print("Login might still be processing...")
        
        
        print(f"Current URL: {page.url}")
        print(f"Current page title: {page.title()}")
        
        # Check if login was successful
        if "login" not in page.url.lower():
            print("Login successful!")
            return True
        else:
            print("Still on login page - login may have failed")
            return False
            
    except Exception as e:
        print(f"An error occurred during login: {str(e)}")
        return False