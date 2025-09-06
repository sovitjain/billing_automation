import json
import boto3
import re

def read_text_file(filename):
    """Read text content from a file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Could not read file {filename}: {e}")

def get_default_prompt():
    """Get default prompt for CPT code prediction"""
    return """
You are a medical coding expert. Analyze the following clinical notes and predict appropriate CPT codes with modifiers.

Rules:
1. Return only valid CPT codes that match the documented services
2. Include appropriate modifiers (25 for E/M with procedure, 59 for distinct procedures, etc.)
3. Return JSON format with the structure below
4. Limit to maximum 6 CPT codes
5. Focus on procedures, evaluations, and treatments documented

Return JSON in this exact format:
[
  {
    "code": "99213",
    "modifier1": "25",
    "modifier2": "",
    "description": "Office visit, established patient, level 3"
  }
]

Clinical Notes:
{notes}

JSON Response:
"""

def get_cpt_codes_from_bedrock(notes, prompt_template, region='us-east-1'):
    """Get CPT code predictions from AWS Bedrock"""
    try:
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name=region)
        
        # Format the prompt with clinical notes
        formatted_prompt = prompt_template.replace('{notes}', notes)
        
        # Prepare the request for Claude
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": formatted_prompt
                }
            ]
        }
        
        # Call Bedrock API
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps(request_body),
            contentType="application/json"
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        if 'content' in response_body and len(response_body['content']) > 0:
            return response_body['content'][0]['text']
        else:
            print("No content in Bedrock response")
            return None
            
    except Exception as e:
        print(f"Bedrock API call failed: {e}")
        return None

def parse_json_response(response_text):
    """Parse JSON response from Bedrock"""
    try:
        if not response_text:
            return None
        
        # Clean the response text
        cleaned_text = response_text.strip()
        
        # Look for JSON array or object
        json_match = re.search(r'\[.*?\]', cleaned_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
        else:
            # Try to find JSON object
            json_match = re.search(r'\{.*?\}', cleaned_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
            else:
                print("No JSON found in response")
                return None
        
        # Parse JSON
        parsed_data = json.loads(json_str)
        return parsed_data
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response_text[:500]}...")
        return None
    except Exception as e:
        print(f"Error parsing response: {e}")
        return None