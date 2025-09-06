# eClinicalWorks Billing Automation with AI-Powered CPT Prediction

This Python automation suite combines web automation with AWS Bedrock AI to streamline the billing workflow in eClinicalWorks, including intelligent CPT code prediction from clinical notes.

## Features

### Core Automation
- **Automated Login**: Two-step login process (username → password)
- **Provider Selection**: Clicks "S" button in top-right corner
- **Date Selection**: Uses calendar widget to select target date
- **Claims Navigation**: Navigates to Claims via hamburger menu
- **Claims Lookup**: Searches for specific claims with date filters

### AI-Powered Code Prediction
- **Clinical Notes Processing**: Reads clinical notes from `notes.txt`
- **AWS Bedrock Integration**: Uses Claude/other LLMs to predict CPT codes
- **Intelligent Code Entry**: Automatically populates predicted CPT codes with modifiers
- **Multi-Row Population**: Handles multiple CPT codes with auto-row creation
- **ICD Code Entry**: Automatically adds appropriate ICD codes

### Advanced Code Handling
- **Dynamic Row Creation**: Uses ECW's built-in row creation (Tab triggers new rows)
- **Modifier Support**: Populates M1 and M2 modifiers in correct columns
- **Multiple CPT Codes**: Processes all predicted codes sequentially
- **Auto-Population**: Leverages ECW's field auto-population features

## Architecture

The system consists of two main modules:

### 1. `web_automation.py` (Main Navigation Module)
- Handles login and navigation to claims
- Manages ECW interface interactions
- Coordinates with CPT population module

### 2. `cpt_population.py` (AI-Powered Code Module)
- Integrates with AWS Bedrock for CPT prediction
- Processes clinical notes and generates structured predictions
- Populates CPT codes and modifiers in ECW interface
- Handles ICD code entry

## Prerequisites

- Python 3.7+
- Playwright library
- AWS Bedrock access with appropriate model permissions
- Valid eClinicalWorks credentials
- Clinical notes file (`notes.txt`)
- Optional custom prompt file (`prompt.txt`)

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

3. Create required files in the same directory as the scripts

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
```

### `notes.txt`
Contains the clinical notes that will be processed by AI:
```
Patient presents with lower back pain, duration 3 weeks.
Physical therapy evaluation and treatment provided.
Electrical stimulation therapy administered.
...
```

### `prompt.txt` (Optional)
Custom prompt template for AI processing:
```
Analyze the following clinical notes and predict appropriate CPT codes.
Return JSON format with code, modifier1, modifier2, and description fields.
[Your custom instructions...]
```

## Workflow

### 1. AI-Powered CPT Prediction
- Reads clinical notes from `notes.txt`
- Sends notes to AWS Bedrock (Claude/other LLMs)
- Processes AI response to extract CPT codes and modifiers
- Validates and structures the predicted codes

### 2. ECW Navigation (Same as before)
- Completes login process
- Navigates to target claim
- Prepares interface for code entry

### 3. Intelligent Code Population
- **First CPT Code**: Populates the "*" row using `input[ng-model="newCPT"]`
- **Subsequent Codes**: Uses Tab-triggered auto-row creation
- **Modifier Handling**: Adds M1 and M2 modifiers to respective columns
- **Auto-Population**: Leverages ECW's field validation and auto-fill

### 4. Code Entry Process
```
CPT Code Entry Sequence:
1. Target "*" row (newCPT field)
2. Enter CPT code (e.g., "99213")
3. Press Tab → ECW auto-populates fields and creates new "*" row
4. Add M1 modifier to column 8 of same row
5. Add M2 modifier to column 9 of same row
6. Repeat for next CPT code using new "*" row
```

## AI Integration Details

### Bedrock Model Support
- **Claude (Anthropic)**: Primary model for clinical note analysis
- **Custom Prompts**: Supports tailored prompt engineering
- **JSON Response Parsing**: Structured code extraction

### Predicted Data Structure
```json
[
  {
    "code": "99213",
    "modifier1": "25",
    "modifier2": "",
    "description": "Office visit, established patient, level 3"
  },
  {
    "code": "97750",
    "modifier1": "",
    "modifier2": "",
    "description": "Physical therapy evaluation"
  }
]
```

## Key Selectors and Field Mapping

### CPT Code Population
- **New CPT Field**: `input[ng-model="newCPT"]` or `#billingClaimIpt34`
- **M1 Modifier**: Column 8 (`td:nth-child(8) input`)
- **M2 Modifier**: Column 9 (`td:nth-child(9) input`)
- **Row Targeting**: `table tbody tr:nth-child(N)` for specific rows

### ICD Code Entry
- **ICD Field**: `input[ng-model="newICD"]`
- **ICD Section**: `h4:has-text("ICD Codes")`

## Usage

1. Prepare clinical notes in `notes.txt`
2. Configure AWS Bedrock access
3. Set up `config.properties`
4. Run the automation:
```bash
python web_automation.py
```

### Expected Output
```
GETTING CPT CODE PREDICTIONS FROM BEDROCK
Loaded notes from notes.txt (1250 characters)
Calling Bedrock API...
Successfully parsed 4 CPT codes from Bedrock response

PREDICTED CPT CODES:
1. CPT: 99213
   Modifier1: 25
   Description: Office visit, established patient

2. CPT: 51784
   Description: Electromyography studies

[Login and navigation process...]

STARTING CPT AND ICD CODE POPULATION
Processing CPT code 1: 99213
Found * row CPT field: input[ng-model="newCPT"]
Added M1: 25 to row 1
Processing CPT code 2: 51784
[...]
```

## Advanced Features

### Modifier Management
- **Automatic Placement**: M1/M2 modifiers placed in correct table columns
- **Row-Specific**: Each CPT code's modifiers stay with their respective row
- **Visual Debugging**: Color-coded field highlighting during population

### Error Handling & Debugging
- **Field Detection**: Multiple selector strategies for robust field finding
- **Screenshot Capture**: Visual debugging at each step
- **Bedrock Failover**: Graceful handling of AI service issues
- **Row Creation Monitoring**: Validates ECW's auto-row creation

### Multiple Code Support
- **Sequential Processing**: Handles 4+ CPT codes automatically
- **Row Auto-Creation**: Leverages ECW's Tab-triggered row creation
- **No Add Button**: Uses native ECW behavior instead of clicking Add

## Troubleshooting

### AI/Bedrock Issues
- **No Response**: Check AWS credentials and Bedrock model access
- **Invalid JSON**: Review prompt.txt formatting
- **Poor Predictions**: Improve clinical notes detail or customize prompt

### Code Population Issues
- **Modifiers in Wrong Column**: Verify table structure hasn't changed
- **Missing Rows**: Ensure ECW's auto-row creation is working
- **Field Not Found**: Check for ECW interface updates

### Debug Screenshots
- `before_cpt_population.png` - State before code entry
- `after_cpt_1_99213.png` - After first CPT code
- `debug_no_field_row_X.png` - Field detection failures

## Customization

### Custom AI Prompts
Create `prompt.txt` with specific instructions:
```
You are a medical coding expert. Analyze clinical notes and return CPT codes.
Focus on E/M codes, procedures, and diagnostic services.
Include appropriate modifiers for same-day services.
```

### Adding New Code Types
Extend the system to handle additional code types by modifying the parsing logic in `cpt_population.py`.

### Different ECW Versions
Update field selectors if ECW interface changes:
```python
# Update selectors in cpt_population.py
code_field_selectors = [
    'your_new_selector',
    'input[ng-model="newCPT"]',  # fallback
]
```

## Security & Compliance

- **AWS Credentials**: Use IAM roles or secure credential management
- **PHI Handling**: Ensure clinical notes comply with HIPAA requirements
- **Audit Trail**: Maintain logs of all automated coding actions
- **Human Oversight**: Validate AI predictions before claim submission

## Performance Optimization

- **Bedrock Caching**: Implement response caching for similar notes
- **Batch Processing**: Process multiple claims in sequence
- **Parallel Execution**: Run multiple browser instances for high volume

## Version History

- **v2.0**: Added AWS Bedrock integration and AI-powered CPT prediction
- **v2.1**: Implemented multiple CPT code support with auto-row creation
- **v2.2**: Added modifier support (M1/M2) with correct column targeting
- **v2.3**: Enhanced error handling and debugging features
- **v1.4**: Base automation (login, navigation, manual code entry)

## Future Enhancements

- Support for additional AI models (GPT-4, etc.)
- Real-time code validation against payer rules
- Integration with coding reference databases
- Batch processing for multiple claims
- Advanced reporting and analytics
