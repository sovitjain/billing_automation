"""
Notes Handler Module

This module handles reading, formatting, and displaying clinical notes
for the ECW automation script.
"""

import os
import sys
from typing import Optional


class NotesHandler:
    """Handles clinical notes operations"""
    
    def __init__(self, notes_file: str = None):
        """
        Initialize the NotesHandler
        
        Args:
            notes_file (str, optional): Path to the notes file (can be None for direct text processing)
        """
        self.notes_file = notes_file
    
    def read_notes(self) -> Optional[str]:
        """
        Read notes from the notes file
        
        Returns:
            str: The content of the notes file, or None if error
        """
        try:
            if not os.path.exists(self.notes_file):
                print(f"Error: {self.notes_file} not found!")
                return None
            
            with open(self.notes_file, 'r', encoding='utf-8') as file:
                content = file.read().strip()
            
            if not content:
                print(f"Warning: {self.notes_file} is empty!")
                return None
            
            print(f"Successfully loaded notes from {self.notes_file} ({len(content)} characters)")
            return content
            
        except Exception as e:
            print(f"Error reading {self.notes_file}: {e}")
            return None
    
    def format_notes(self, notes_text: str) -> str:
        """
        Format multi-line notes by replacing escape sequences
        
        Args:
            notes_text (str): Raw notes text
            
        Returns:
            str: Formatted notes text
        """
        if not notes_text:
            return ""
        
        # Replace literal \n with actual newlines
        formatted_notes = notes_text.replace('\\n', '\n')
        # Also handle other common escape sequences
        formatted_notes = formatted_notes.replace('\\t', '\t')
        formatted_notes = formatted_notes.replace('\\r', '\r')
        
        return formatted_notes.strip()
    
    def display_notes(self, max_length: int = 1000, show_full: bool = False) -> None:
        """
        Display the clinical notes with formatting
        
        Args:
            max_length (int): Maximum characters to display (if show_full is False)
            show_full (bool): Whether to show the full notes or truncate
        """
        try:
            notes_content = self.read_notes()
            if not notes_content:
                print("No notes available to display")
                return
            
            formatted_notes = self.format_notes(notes_content)
            
            print("=" * 50)
            print(f"CLINICAL NOTES FROM {self.notes_file.upper()}:")
            print("=" * 50)
            
            if show_full or len(formatted_notes) <= max_length:
                print(formatted_notes)
            else:
                print(formatted_notes[:max_length] + "...")
                print(f"\n[Note: Showing first {max_length} characters of {len(formatted_notes)} total]")
            
            print("=" * 50)
            
        except Exception as e:
            print(f"Error displaying notes: {e}")
    
    def validate_notes_file(self) -> bool:
        """
        Validate that the notes file exists and has content
        
        Returns:
            bool: True if notes file is valid, False otherwise
        """
        if not os.path.exists(self.notes_file):
            print(f"Validation failed: {self.notes_file} does not exist")
            return False
        
        try:
            with open(self.notes_file, 'r', encoding='utf-8') as file:
                content = file.read().strip()
            
            if not content:
                print(f"Validation failed: {self.notes_file} is empty")
                return False
            
            print(f"Validation passed: {self.notes_file} contains {len(content)} characters")
            return True
            
        except Exception as e:
            print(f"Validation failed: Error reading {self.notes_file}: {e}")
            return False
    
    def create_sample_notes(self) -> bool:
        """
        Create a sample notes.txt file if it doesn't exist
        
        Returns:
            bool: True if file was created successfully, False otherwise
        """
        if os.path.exists(self.notes_file):
            print(f"{self.notes_file} already exists")
            return True
        
        sample_notes = """Patient: Test, Manu
Date of Service: [Date]
Chief Complaint: Follow-up visit

History of Present Illness:
Patient presents for routine follow-up. Reports feeling well overall.
No acute complaints at this time.

Physical Examination:
Vital Signs: Stable
General: Well-appearing, no acute distress
HEENT: Normal
Cardiovascular: Regular rate and rhythm
Respiratory: Clear to auscultation bilaterally
Abdomen: Soft, non-tender

Assessment and Plan:
1. Routine follow-up - continue current management
2. Patient education provided
3. Return to clinic in 3 months or as needed

Provider: [Provider Name]
"""
        
        try:
            with open(self.notes_file, 'w', encoding='utf-8') as file:
                file.write(sample_notes)
            
            print(f"Created sample {self.notes_file}")
            print("Please edit this file with actual clinical notes before running the automation")
            return True
            
        except Exception as e:
            print(f"Error creating sample {self.notes_file}: {e}")
            return False
    
    def extract_clinical_notes_from_html(self, html_content: str) -> str:
        """
        Extract clinical notes from ECW Progress Notes HTML structure
        
        Args:
            html_content (str): Raw HTML content from Progress Notes dialog
            
        Returns:
            str: Extracted and formatted clinical notes
        """
        try:
            import re
            
            if not html_content:
                return ""
            
            print("Analyzing HTML content for clinical notes extraction...")
            print(f"HTML content length: {len(html_content)} characters")
            
            # First, look for the specific table structure from your document
            # Look for tables with prisma-section attributes or clinical content patterns
            
            clinical_content = ""
            
            # Pattern 1: Look for the patient table and subsequent clinical sections
            patient_pattern = r'<b>Patient:\s*</b>([^<]+).*?<span[^>]*><b>Subjective:</b></span>(.*?)(?=<span[^>]*><b>Assessment:</b></span>|$)'
            patient_match = re.search(patient_pattern, html_content, re.DOTALL | re.IGNORECASE)
            
            if patient_match:
                print("Found patient and subjective section using pattern 1")
                patient_name = patient_match.group(1).strip()
                subjective_content = patient_match.group(2)
                clinical_content = f"Patient: {patient_name}\n\nSubjective:\n{self._clean_html_content(subjective_content)}"
            
            # Pattern 2: Look for HPI section specifically
            hpi_pattern = r'<b>HPI:\s*</b>(.*?)(?=<b>(?:Objective|Examination|Assessment):|$)'
            hpi_match = re.search(hpi_pattern, html_content, re.DOTALL | re.IGNORECASE)
            
            if hpi_match:
                print("Found HPI section")
                hpi_content = self._clean_html_content(hpi_match.group(1))
                if clinical_content:
                    clinical_content += f"\n\nHPI:\n{hpi_content}"
                else:
                    clinical_content = f"HPI:\n{hpi_content}"
            
            # Pattern 3: Look for PFPT content specifically (from your document)
            pfpt_pattern = r'(PFPT[^<]*(?:<[^>]*>[^<]*)*?(?:pelvic\s+(?:floor|pain)|physical\s+therapy)[^<]*(?:<[^>]*>[^<]*)*?(?:stimulation|therapy|muscles)[^<]*(?:<[^>]*>[^<]*)*)'
            pfpt_matches = re.findall(pfpt_pattern, html_content, re.DOTALL | re.IGNORECASE)
            
            if pfpt_matches:
                print(f"Found {len(pfpt_matches)} PFPT sections")
                pfpt_content = self._clean_html_content(' '.join(pfpt_matches))
                if clinical_content:
                    clinical_content += f"\n\nPFPT Details:\n{pfpt_content}"
                else:
                    clinical_content = f"PFPT Details:\n{pfpt_content}"
            
            # Pattern 4: Look for examination section
            exam_pattern = r'<b>Examination:[^<]*</b>(.*?)(?=<b>(?:Assessment|Plan):|$)'
            exam_match = re.search(exam_pattern, html_content, re.DOTALL | re.IGNORECASE)
            
            if exam_match:
                print("Found Examination section")
                exam_content = self._clean_html_content(exam_match.group(1))
                if clinical_content:
                    clinical_content += f"\n\nExamination:\n{exam_content}"
                else:
                    clinical_content = f"Examination:\n{exam_content}"
            
            # Pattern 5: Look for assessment section
            assessment_pattern = r'<b>Assessment:\s*</b>(.*?)(?=<b>(?:Plan|Treatment):|$)'
            assessment_match = re.search(assessment_pattern, html_content, re.DOTALL | re.IGNORECASE)
            
            if assessment_match:
                print("Found Assessment section")
                assessment_content = self._clean_html_content(assessment_match.group(1))
                if clinical_content:
                    clinical_content += f"\n\nAssessment:\n{assessment_content}"
                else:
                    clinical_content = f"Assessment:\n{assessment_content}"
            
            # Pattern 6: Look for procedure codes section
            procedure_pattern = r'<b>Procedure\s+Codes:</b>(.*?)(?=</table>|<b>[^>]*</b>|$)'
            procedure_match = re.search(procedure_pattern, html_content, re.DOTALL | re.IGNORECASE)
            
            if procedure_match:
                print("Found Procedure Codes section")
                procedure_content = self._clean_html_content(procedure_match.group(1))
                if clinical_content:
                    clinical_content += f"\n\nProcedure Codes:\n{procedure_content}"
                else:
                    clinical_content = f"Procedure Codes:\n{procedure_content}"
            
            # Pattern 7: Look for visit code
            visit_pattern = r'<b>Visit\s+Code:</b>(.*?)(?=</table>|<b>[^>]*</b>|$)'
            visit_match = re.search(visit_pattern, html_content, re.DOTALL | re.IGNORECASE)
            
            if visit_match:
                print("Found Visit Code section")
                visit_content = self._clean_html_content(visit_match.group(1))
                if clinical_content:
                    clinical_content += f"\n\nVisit Code:\n{visit_content}"
                else:
                    clinical_content = f"Visit Code:\n{visit_content}"
            
            # If we found clinical content, return it
            if clinical_content and len(clinical_content.strip()) > 100:
                print(f"Successfully extracted clinical content: {len(clinical_content)} characters")
                return clinical_content.strip()
            
            # Fallback: Look for any tables with clinical keywords
            print("Primary patterns failed, trying fallback extraction...")
            
            # Look for any content containing clinical keywords
            clinical_keywords = ['patient', 'pelvic', 'pain', 'therapy', 'stimulation', 'examination', 'assessment', 'pfpt']
            
            # Extract text from table cells that contain clinical keywords
            table_pattern = r'<td[^>]*>(.*?)</td>'
            table_matches = re.findall(table_pattern, html_content, re.DOTALL | re.IGNORECASE)
            
            relevant_content = []
            for match in table_matches:
                cleaned = self._clean_html_content(match).strip()
                if len(cleaned) > 20 and any(keyword.lower() in cleaned.lower() for keyword in clinical_keywords):
                    relevant_content.append(cleaned)
            
            if relevant_content:
                fallback_content = '\n'.join(relevant_content[:20])  # Limit to first 20 relevant pieces
                print(f"Fallback extraction found: {len(fallback_content)} characters")
                return fallback_content
            
            print("No clinical content could be extracted from HTML")
            return "No clinical notes found in the provided HTML content"
                    
        except Exception as e:
            print(f"Error extracting clinical notes from HTML: {e}")
            return f"Error parsing clinical notes: {e}"
                    
        except Exception as e:
            print(f"Error extracting clinical notes from HTML: {e}")
            return f"Error parsing clinical notes: {e}"
    
    def _clean_html_content(self, content: str) -> str:
        """Clean HTML tags and format content"""
        import re
        
        if not content:
            return ""
        
        # Remove HTML tags but preserve structure
        content = re.sub(r'<[^>]+>', ' ', content)
        
        # Clean up HTML entities
        html_entities = {
            '&nbsp;': ' ',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&apos;': "'"
        }
        
        for entity, replacement in html_entities.items():
            content = content.replace(entity, replacement)
        
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n', '\n', content)
        
        # Clean up excessive spacing
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:  # Only keep non-empty lines
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
        """
        Get a summary of the notes file
        
        Returns:
            dict: Summary information about the notes
        """
        summary = {
            'file_exists': False,
            'file_size': 0,
            'character_count': 0,
            'line_count': 0,
            'word_count': 0,
            'is_valid': False
        }
        
        try:
            if os.path.exists(self.notes_file):
                summary['file_exists'] = True
                summary['file_size'] = os.path.getsize(self.notes_file)
                
                with open(self.notes_file, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                summary['character_count'] = len(content)
                summary['line_count'] = len(content.splitlines())
                summary['word_count'] = len(content.split())
                summary['is_valid'] = len(content.strip()) > 0
            
        except Exception as e:
            print(f"Error getting notes summary: {e}")
        
        return summary


def main():
    """
    Main function for testing the NotesHandler
    """
    handler = NotesHandler()
    
    print("Notes Handler Test")
    print("-" * 30)
    
    # Check if notes file exists
    if not handler.validate_notes_file():
        print("Creating sample notes file...")
        handler.create_sample_notes()
    
    # Display summary
    summary = handler.get_notes_summary()
    print(f"\nNotes File Summary:")
    print(f"File exists: {summary['file_exists']}")
    print(f"File size: {summary['file_size']} bytes")
    print(f"Characters: {summary['character_count']}")
    print(f"Lines: {summary['line_count']}")
    print(f"Words: {summary['word_count']}")
    print(f"Valid: {summary['is_valid']}")
    
    # Display notes
    print("\nDisplaying notes:")
    handler.display_notes()


if __name__ == "__main__":
    main()