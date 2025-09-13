# eClinicalWorks Billing Automation with AI-Powered CPT Prediction

This Python automation suite combines web automation with AWS Bedrock AI to streamline the billing workflow in eClinicalWorks, including intelligent CPT code prediction from clinical notes with support for multiple insurance plans.

## Features

### Core Automation
- **Automated Login**: Two-step login process (username → password)
- **Dynamic Date Selection**: Configurable target dates with proper month/day/year parsing
- **Claims Navigation**: Navigates to Claims via hamburger menu
- **Configurable Claims Lookup**: Searches for specific claims with configurable claim IDs
- **Retry Logic**: 3-attempt retry mechanism for progress notes extraction

### AI-Powered Code Prediction
- **Progress Notes Extraction**: Extracts clinical notes directly from ECW interface
- **AWS Bedrock Integration**: Uses Claude/other LLMs to predict CPT codes
- **Insurance Plan Support**: Separate prompts for Commercial vs Medicare plans
- **Intelligent Code Entry**: Automatically populates predicted CPT codes with modifiers
- **Multi-Row Population**: Handles multiple CPT codes with auto-row creation
- **ICD Code Entry**: Automatically adds appropriate ICD codes

### Advanced Code Handling
- **Dynamic Row Creation**: Uses ECW's built-in row creation (Tab triggers new rows)
- **Modifier Support**: Populates M1 and M2 modifiers in correct columns
- **Multiple CPT Codes**: Processes all predicted codes sequentially
- **Auto-Population**: Leverages ECW's field auto-population features
- **Plan-Specific Rules**: Different CPT code sets for Commercial vs Medicare

## Architecture

The system consists of modular components:

### 1. `web_automation.py` (Main Orchestrator)
- Handles login and navigation to claims
- Manages ECW interface interactions
- Coordinates with all other modules
- Implements retry logic for progress notes extraction

### 2. `claims_lookup.py` (Claims Management)
- Configurable claim ID lookup
- Status setting (Pending)
- Claims search and selection

### 3. `progress_notes_extractor.py` (Notes Extraction)
- Extracts clinical notes from ECW Progress Notes section
- Multiple extraction strategies for reliability
- Anorectal manometry status detection

### 4. `cpt_population.py` (AI-Powered Code Module)
- Integrates with AWS Bedrock for CPT prediction
- Insurance plan-specific processing
- Populates CPT codes and modifiers in ECW interface
- Handles ICD code entry

### 5. `ecw_navigation.py` (Navigation Utilities)
- Date selection with dynamic month parsing
- Menu navigation utilities
- Calendar interaction logic

## Prerequisites

- Python 3.7+
- Playwright library
- AWS Bedrock access with appropriate model permissions
- Valid eClinicalWorks credentials

## Installation

1. Install required packages:
```bash
pip install playwright boto3 configparser
playwright install chromium
```

2. Configure AWS credentials for Bedrock access:
```bash
aws configure
# or set environment variables AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
```

## Configuration

### `config.properties`
```ini
[DEFAULT]
username=your_username
password=your_password
url=https://your_ecw_url/mobiledoc/jsp/webemr/login/newLogin.jsp
provider_name=LASTNAME,FIRSTNAME
target_date=MM-DD-YYYY
aws_region=us-east-1

[BROWSER]
headless=false
screenshot=true
wait_timeout=5000

[CLAIMS]
claim_id=12345
insurance_plan=Commercial
```

### Insurance Plan Prompts

The system supports separate prompt files for different insurance plans:

- **`prompt_commercial.txt`** - Commercial plan specific rules and CPT codes
- **`prompt_medicare.txt`** - Medicare plan rules with visit-based coding
- **`prompt.txt`** - Fallback/default prompt

### Commercial Plan Rules (`prompt_commercial.txt`)
```
Required CPT codes:
- CPT 99213 with modifier 25 (office visit)
- CPT 91122 (anorectal manometry) - if performed
- CPT 51784 (urodynamic procedure)
- CPT 97750 with modifier 59 and GP (physical therapy)
- CPT 97032 with modifier 59 and GP (electrical stimulation)
```

### Medicare Plan Rules (`prompt_medicare.txt`)
```
Visit-based coding:
- 1st visit: 99213, 91122, 97750, 97032
- 2nd visit: 99213, 51784, 97032
- 3rd+ visits: 99213, 90912, 97032
```

## Workflow

### 1. Configuration-Based Setup
- Reads all settings from `config.properties`
- Selects appropriate prompt file based on insurance plan
- Validates required files and configurations

### 2. ECW Navigation
- Automated login with credentials from config
- Dynamic date selection using configured target_date
- Claims lookup using configured claim_id

### 3. Progress Notes Extraction (with Retry)
- Attempts to extract notes from ECW Progress Notes section
- Retries up to 3 times with 2-second delays
- Prompts for human intervention if all attempts fail
- **No automatic fallback to notes.txt**

### 4. AI-Powered CPT Prediction
- Sends extracted notes to AWS Bedrock
- Uses insurance plan-specific prompt
- Validates and structures predicted codes
- Handles different expected code counts (Commercial: 4+, Medicare: 3+)

### 5. Intelligent Code Population
- Populates CPT codes with modifiers
- Creates new rows automatically using ECW's Tab behavior
- Adds ICD codes as needed

## Key Improvements

### Configurable Parameters
- **Claim ID**: Set in `config.properties` under `[CLAIMS] claim_id`
- **Insurance Plan**: `Commercial` or `Medicare` affects CPT code selection
- **Target Date**: Dynamic month/day/year parsing (no more hardcoded August)
- **All credentials**: Stored in config file, not hardcoded

### Robust Progress Notes Extraction
- **3 retry attempts** with delays between attempts
- **Human intervention prompt** when extraction fails
- **No silent fallback** to notes.txt file
- **Detailed logging** of each extraction attempt

### Insurance Plan Intelligence
- **Plan-specific prompts**: Separate files for Commercial vs Medicare
- **Different CPT expectations**: Commercial needs 4+ codes, Medicare needs 3+
- **Plan-appropriate rules**: Visit-based coding for Medicare, comprehensive for Commercial

### Error Handling
- **Unicode character fixes**: No more encoding errors in output
- **Integer CPT code handling**: Handles numeric CPT codes from Bedrock
- **Graceful failures**: Clear error messages and user control

## Usage

1. Configure `config.properties` with your settings
2. Ensure AWS Bedrock access is configured
3. Run the automation:
```bash
python web_automation.py
```

### Testing Individual Components

Test Bedrock prediction separately:
```bash
python test_bedrock_local.py
```

## Expected Output

```
================================================================================
ECW WEB AUTOMATION - MODULAR VERSION
================================================================================
Configuration loaded:
  - Headless mode: False
  - Screenshots: True
  - Target date: 09-06-2025
  - Claim number: 39359
  - Insurance plan: Commercial

============================================================
STEP 1: ECW LOGIN
============================================================
[Login process...]

============================================================
STEP 5: CLAIMS LOOKUP WORKFLOW
============================================================
Looking for claim# 39359...
Successfully clicked on claim# 39359

============================================================
STEP 6: EXTRACT PROGRESS NOTES
============================================================
Progress Notes extraction attempt 1/3
SUCCESS: Progress Notes extracted successfully (4197 characters)

============================================================
STEP 7: POPULATE CPT AND ICD CODES
============================================================
Loaded Commercial-specific prompt from prompt_commercial.txt
SUCCESS: Received sufficient CPT codes (5) with all code fields populated

PREDICTED CPT CODES:
1. CPT: 99213, Modifier1: 25
2. CPT: 91122
3. CPT: 51784
4. CPT: 97750, Modifier1: 59, Modifier2: GP
5. CPT: 97032, Modifier1: 59, Modifier2: GP
```

## File Structure

```
billing_automation/
├── web_automation.py          # Main orchestrator
├── claims_lookup.py           # Claims search and selection
├── progress_notes_extractor.py # Notes extraction from ECW
├── cpt_population.py          # AI-powered CPT prediction
├── ecw_navigation.py          # Navigation utilities
├── bedrock_cpt_predictor.py   # Bedrock integration
├── test_bedrock_local.py      # Testing utility
├── config.properties          # Configuration file
├── prompt_commercial.txt      # Commercial plan prompt
├── prompt_medicare.txt        # Medicare plan prompt
├── prompt.txt                 # Fallback prompt
└── README.md                  # This file
```

## Security & Compliance

- **Credential Management**: All sensitive data in config.properties
- **PHI Handling**: Clinical notes extracted securely from ECW
- **Audit Trail**: Detailed logging of all automation steps
- **Human Oversight**: Retry logic ensures human control when needed

## Troubleshooting

### Common Issues

1. **Progress Notes Extraction Fails**
   - Check if Progress Notes button is visible in ECW
   - Verify page has fully loaded before extraction
   - Use manual intervention prompt to investigate

2. **Wrong Insurance Plan Codes**
   - Verify `insurance_plan` setting in config.properties
   - Check that correct prompt file exists (prompt_commercial.txt or prompt_medicare.txt)

3. **Date Selection Issues**
   - Ensure target_date format is MM-DD-YYYY
   - Check that target month/year are valid

4. **Claim Not Found**
   - Verify claim_id in config.properties
   - Check date range includes the claim
   - Ensure claim status allows lookup

### Debug Files
- `ecw_final_state.png` - Final state screenshot
- `automation_error.png` - Error state screenshot
- `bedrock_test_results.json` - AI prediction results

## Version History

- **v3.0**: Complete modularization with configurable parameters
- **v2.9**: Added insurance plan-specific prompts and retry logic
- **v2.8**: Implemented configurable claim IDs and dates
- **v2.7**: Enhanced progress notes extraction with retry mechanism
- **v2.6**: Fixed Unicode encoding and integer CPT code issues
- **v2.5**: Added Medicare vs Commercial plan support
- **v2.0**: Added AWS Bedrock integration and AI-powered CPT prediction

## Future Enhancements

- Support for additional insurance plan types
- Bulk claim processing capabilities
- Integration with coding compliance databases
- Advanced anorectal manometry detection rules
- Real-time code validation against payer policies