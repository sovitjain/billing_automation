# eClinicalWorks Billing Automation

This Python script automates the billing workflow in eClinicalWorks, including login, navigation, claims lookup, and code entry.

## Features

- **Automated Login**: Two-step login process (username → password)
- **Provider Selection**: Clicks "S" button in top-right corner
- **Date Selection**: Uses calendar widget to select target date
- **Claims Navigation**: Navigates to Claims via hamburger menu
- **Claims Lookup**: Searches for specific claims with date filters
- **Code Entry**: Automatically adds CPT and ICD codes with auto-population

## Prerequisites

- Python 3.7+
- Playwright library
- Valid eClinicalWorks credentials
- Access to eClinicalWorks system

## Installation

1. Install required packages:
```bash
pip install playwright
playwright install chromium
```

2. Create `config.properties` file in the same directory as the script

## Configuration

Create a `config.properties` file with the following structure:

```ini
[DEFAULT]
username=your_username
password=your_password
url=https://your_ecw_url/mobiledoc/jsp/webemr/login/newLogin.jsp
provider_name=LASTNAME,FIRSTNAME
target_date=MM-DD-YYYY

[BROWSER]
headless=false
screenshot=true
wait_timeout=5000
```

### Configuration Parameters

- **username**: Your eClinicalWorks username
- **password**: Your eClinicalWorks password
- **url**: Full URL to the eClinicalWorks login page
- **provider_name**: Provider name in "LASTNAME,FIRSTNAME" format
- **target_date**: Date to search for in "MM-DD-YYYY" format
- **headless**: Set to `true` to run browser in background
- **screenshot**: Set to `true` to capture screenshots for debugging
- **wait_timeout**: Timeout value in milliseconds

## Workflow

### 1. Login Process
- Navigates to eClinicalWorks login page
- Enters username and clicks Next
- Enters password on second screen
- Completes two-step authentication

### 2. Dashboard Navigation
- Clicks "S" button in top-right corner
- Closes any open submenus
- Uses calendar widget to select target date

### 3. Claims Access
- Opens hamburger menu (top-left corner)
- Navigates to Billing section
- Clicks on Claims submenu
- Sets Service Date FROM and TO fields
- Performs claims lookup

### 4. Claims Processing
- Selects "All Claims" from status dropdown
- Chooses specific patient (Test, Manu)
- Clicks main Lookup button
- Opens specific claim (e.g., claim# 38000)

### 5. Code Entry
- **CPT Code**: Enters "99213" in CPT/HCPCS Code field and presses Tab
- **ICD Code**: Enters "A42.1" in ICD Codes section and presses Tab
- Auto-population occurs for related fields

## Key Selectors Used

### Navigation Elements
- Hamburger menu: `#jellybean-panelLink4.navgator.mainMenu`
- Billing menu: `.icon.nav-label.icon-label-bill`
- Claims icon: `.svgicon.svg-document1`

### Form Elements
- Calendar widget: `.icon.icon-inputcalender`
- CPT Code field: `#billingClaimIpt34`
- ICD Code field: `input[ng-model="newICD"]`
- Claim status: `#claimStatusCodeId`
- Lookup button: `#btnclaimlookup`

## Usage

1. Ensure `config.properties` is properly configured
2. Run the script:
```bash
python web_automation.py
```

3. The browser will open and automation will begin
4. Monitor console output for progress and debugging information
5. Screenshots will be saved at key steps (if enabled)

## Screenshots Generated

- `ecw_login_before.png` - Initial login page
- `ecw_login_filled.png` - After entering username
- `ecw_password_page.png` - Password entry page
- `ecw_password_filled.png` - After entering password
- `ecw_login_after.png` - After successful login
- `ecw_dashboard.png` - Main dashboard
- `ecw_final_state.png` - Final state after automation

## Error Handling

The script includes comprehensive error handling:
- Multiple selector attempts for each element
- Graceful fallbacks if primary methods fail
- Detailed logging for troubleshooting
- Screenshot capture on errors

## Debugging Features

- **Verbose logging**: Shows each step of the automation process
- **URL/Title tracking**: Monitors page changes
- **Element detection**: Reports when elements are found or missing
- **Screenshot capture**: Visual record of automation progress

## Troubleshooting

### Common Issues

1. **Login fails**: Check username/password in config
2. **Calendar not found**: Verify target_date format (MM-DD-YYYY)
3. **Claims not found**: Ensure provider_name matches exactly
4. **Code entry fails**: Check if claim is in editable state

### Debug Information

The script provides detailed debug output including:
- Current page URLs
- Page titles
- Element visibility status
- Action completion confirmations

## Customization

### Adding New Codes

To add different CPT or ICD codes, modify the script:

```python
# For CPT codes
code_field.fill("your_cpt_code")

# For ICD codes  
icd_field.fill("your_icd_code")
```

### Changing Date Format

Update the `target_date` parsing in the script if using different date formats.

### Adding New Providers

Update the `provider_name` in config.properties with the correct format.

## Security Notes

- Keep `config.properties` secure and never commit credentials to version control
- Use environment variables for sensitive information in production
- Regularly update passwords and review access logs

## Limitations

- Designed specifically for eClinicalWorks interface
- Requires specific element IDs and classes (may need updates if UI changes)
- Limited to current workflow (login → claims → code entry)
- Browser must remain visible when `headless=false`

## Support

For issues or questions:
1. Check console output for error messages
2. Review screenshot files for visual debugging
3. Verify config.properties settings
4. Ensure eClinicalWorks interface hasn't changed

## Version History

- **v1.0**: Initial automation with login and basic navigation
- **v1.1**: Added calendar widget and date selection
- **v1.2**: Implemented claims navigation and lookup
- **v1.3**: Added CPT and ICD code entry with auto-population
- **v1.4**: Enhanced error handling and debugging features