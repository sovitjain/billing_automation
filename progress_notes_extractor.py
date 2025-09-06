"""
Progress Notes Extractor Module
Handles extraction of clinical notes from ECW Progress Notes dialog
"""

def find_progress_notes_button(page):
    """
    Find and click the Progress Notes button
    
    Args:
        page: Playwright page object
    
    Returns:
        bool: True if button found and clicked, False otherwise
    """
    try:
        print("Looking for Progress Notes button...")
        
        prog_notes_selectors = [
            'button:has-text("Prog. Notes")',
            'input[value*="Prog. Notes"]',
            'button[title*="Progress Notes"]',
            '.btn:has-text("Prog. Notes")',
            'button:has-text("Progress Notes")',
            'input[value="Prog. Notes"]'
        ]
        
        prog_notes_clicked = False
        for selector in prog_notes_selectors:
            try:
                prog_button = page.locator(selector).first
                if prog_button.is_visible() and prog_button.is_enabled():
                    print(f"Found Progress Notes button: {selector}")
                    prog_button.click()
                    page.wait_for_timeout(3000)
                    print("Successfully clicked Progress Notes button")
                    prog_notes_clicked = True
                    break
            except Exception as e:
                print(f"Progress Notes selector {selector} failed: {e}")
                continue
        
        if not prog_notes_clicked:
            print("Could not find or click Progress Notes button")
            # Try to find any button with "Prog" in the text
            try:
                all_buttons = page.locator('button, input[type="button"], input[type="submit"]').all()
                print(f"Found {len(all_buttons)} buttons, checking for Progress Notes...")
                for i, button in enumerate(all_buttons[:10]):  # Check first 10 buttons
                    try:
                        button_text = button.text_content() or ""
                        button_value = button.get_attribute('value') or ""
                        if 'prog' in button_text.lower() or 'prog' in button_value.lower():
                            print(f"Found potential Progress button {i}: text='{button_text}', value='{button_value}'")
                            button.click()
                            page.wait_for_timeout(3000)
                            prog_notes_clicked = True
                            break
                    except:
                        continue
            except Exception as e:
                print(f"Button search failed: {e}")
        
        return prog_notes_clicked
        
    except Exception as e:
        print(f"Error finding Progress Notes button: {e}")
        return False

def extract_iframe_content(page, screenshot=True):
    """
    Extract clinical content from iframes in Progress Notes dialog
    
    Args:
        page: Playwright page object
        screenshot: Whether to take screenshots and save debug files
    
    Returns:
        tuple: (clinical_notes, success_flag)
    """
    try:
        print("Starting iframe content extraction...")
        
        # Wait for Progress Notes dialog to fully load
        page.wait_for_timeout(5000)
        
        # Find all iframes
        iframes = page.locator('iframe').all()
        print(f"Found {len(iframes)} iframes to analyze")
        
        clinical_content = None
        notes_extracted = False
        
        for i, iframe in enumerate(iframes):
            try:
                print(f"\n--- Analyzing iframe {i} ---")
                
                # Get iframe attributes for debugging
                src = iframe.get_attribute('src') or 'No src'
                iframe_id = iframe.get_attribute('id') or 'No id'
                name = iframe.get_attribute('name') or 'No name'
                
                print(f"Iframe {i}: src='{src}', id='{iframe_id}', name='{name}'")
                
                # Try to access iframe content - focus on ProgNoteViwerFrame
                iframe_html = ""
                try:
                    # Skip iframes that are clearly not progress notes
                    if 'ProgNote' not in iframe_id and 'progNote' not in name.lower() and 'progress' not in name.lower():
                        print(f"Iframe {i}: Skipping non-progress-note iframe")
                        continue
                    
                    print(f"Iframe {i}: This looks like a progress notes iframe, processing...")
                    
                    # Try different approaches to access iframe content
                    iframe_frame = None
                    
                    # Method 1: Use content_frame()
                    try:
                        iframe_frame = iframe.content_frame()
                        if iframe_frame:
                            print(f"Iframe {i}: Got content frame via content_frame()")
                    except Exception as e:
                        print(f"Iframe {i}: content_frame() failed: {e}")
                    
                    # Method 2: Try getting frame by name 
                    if not iframe_frame and name != 'No name':
                        try:
                            iframe_frame = page.frame(name=name)
                            if iframe_frame:
                                print(f"Iframe {i}: Got frame via name")
                        except Exception as e:
                            print(f"Iframe {i}: frame by name failed: {e}")
                    
                    # Method 3: Try getting frame by URL or ID
                    if not iframe_frame:
                        try:
                            # Get all frames and find the matching one
                            all_frames = page.frames
                            for frame in all_frames:
                                if frame.name == name or iframe_id in frame.url:
                                    iframe_frame = frame
                                    print(f"Iframe {i}: Found frame in frames list")
                                    break
                        except Exception as e:
                            print(f"Iframe {i}: frames iteration failed: {e}")
                    
                    if not iframe_frame:
                        print(f"Iframe {i}: Could not access frame content")
                        continue
                    
                    # Wait for content to load
                    try:
                        iframe_frame.wait_for_load_state('networkidle', timeout=5000)
                        print(f"Iframe {i}: Frame loaded")
                    except:
                        print(f"Iframe {i}: Load timeout, proceeding anyway")
                    
                    # Get the content using proper Frame methods
                    try:
                        iframe_html = iframe_frame.content()
                        print(f"Iframe {i}: Got content via content() - {len(iframe_html)} characters")
                    except Exception as content_error1:
                        print(f"Iframe {i}: content() failed: {content_error1}")
                        try:
                            # Try getting inner HTML of body
                            body_locator = iframe_frame.locator('body')
                            if body_locator.count() > 0:
                                iframe_html = body_locator.inner_html()
                                print(f"Iframe {i}: Got content via body inner_html - {len(iframe_html)} characters")
                            else:
                                # Try getting all HTML
                                html_locator = iframe_frame.locator('html')
                                if html_locator.count() > 0:
                                    iframe_html = html_locator.inner_html()
                                    print(f"Iframe {i}: Got content via html inner_html - {len(iframe_html)} characters")
                                else:
                                    print(f"Iframe {i}: No body or html elements found")
                                    continue
                        except Exception as content_error2:
                            print(f"Iframe {i}: inner_html methods failed: {content_error2}")
                            try:
                                # Last resort - try to get text content
                                iframe_html = iframe_frame.locator('*').all_text_contents()
                                iframe_html = ' '.join(iframe_html) if isinstance(iframe_html, list) else str(iframe_html)
                                print(f"Iframe {i}: Got text content - {len(iframe_html)} characters")
                            except Exception as content_error3:
                                print(f"Iframe {i}: All content extraction methods failed: {content_error3}")
                                continue
                    
                except Exception as frame_error:
                    print(f"Iframe {i}: Error accessing frame - {frame_error}")
                    continue
                
                # Process iframe content
                if iframe_html:
                    print(f"Iframe {i}: Processing {len(iframe_html)} characters of HTML content")
                
                # Check for clinical content markers
                clinical_markers = [
                    'Test, Manu',
                    'Patient:',
                    'HPI:',
                    'PFPT',
                    'Subjective:',
                    'Assessment:',
                    'Examination:',
                    'Pelvic Pain',
                    'physical therapy',
                    'electrical stimulation'
                ]
                
                found_markers = []
                for marker in clinical_markers:
                    if marker in iframe_html:
                        found_markers.append(marker)
                
                if found_markers:
                    print(f"*** Iframe {i}: CLINICAL CONTENT FOUND! ***")
                    print(f"Found markers: {found_markers}")
                    clinical_content = iframe_html
                    notes_extracted = True
                    
                    # Also get text content for verification
                    try:
                        iframe_text = iframe_content.locator('body').text_content()
                        print(f"Iframe {i}: Text length = {len(iframe_text)} characters")
                        
                        # Save text content
                        if screenshot:
                            with open(f'iframe_{i}_text.txt', 'w', encoding='utf-8') as f:
                                f.write(iframe_text)
                            print(f"Iframe {i}: Text saved to iframe_{i}_text.txt")
                        
                    except Exception as text_error:
                        print(f"Iframe {i}: Could not extract text: {text_error}")
                    
                    break  # Found the clinical content!
                    
                else:
                    print(f"Iframe {i}: No clinical markers found")
                    # Show a preview of what's in this iframe
                    preview = iframe_html[:500].replace('\n', ' ').replace('\t', ' ')
                    print(f"Iframe {i} preview: {preview}...")
                
            except Exception as iframe_error:
                print(f"Iframe {i}: Error - {iframe_error}")
                continue
        
        if notes_extracted and clinical_content:
            print(f"\n*** SUCCESS: Found clinical content in iframe ***")
            return clinical_content, True
        else:
            print(f"\n*** NO CLINICAL CONTENT FOUND in any iframe ***")
            return None, False
            
    except Exception as e:
        print(f"Error in iframe extraction: {e}")
        return None, False

def close_progress_notes_dialog(page):
    """
    Close the Progress Notes dialog
    
    Args:
        page: Playwright page object
    
    Returns:
        bool: True if dialog closed successfully, False otherwise
    """
    try:
        print("Closing Progress Notes dialog...")
        close_selectors = [
            'button:has-text("Close")',
            'button:has-text("×")',
            '.close',
            '[aria-label="Close"]',
            '.modal-close',
            'button.close'
        ]
        
        dialog_closed = False
        for close_selector in close_selectors:
            try:
                close_button = page.locator(close_selector).first
                if close_button.is_visible():
                    print(f"Closing Progress Notes using: {close_selector}")
                    close_button.click()
                    page.wait_for_timeout(1000)
                    dialog_closed = True
                    break
            except:
                continue
        
        if not dialog_closed:
            print("Could not find close button, pressing Escape key")
            try:
                page.keyboard.press('Escape')
                page.wait_for_timeout(1000)
                dialog_closed = True
            except:
                pass
        
        return dialog_closed
        
    except Exception as e:
        print(f"Error closing Progress Notes dialog: {e}")
        return False

def extract_progress_notes(page, screenshot=True):
    """
    Complete Progress Notes extraction workflow
    
    Args:
        page: Playwright page object
        screenshot: Whether to take screenshots and save debug files
    
    Returns:
        str: Extracted clinical notes or error message
    """
    try:
        
        print("=" * 60)
        print("EXTRACTING CLINICAL NOTES FROM PROGRESS NOTES")
        print("=" * 60)
        
        # Step 1: Find and click Progress Notes button
        if not find_progress_notes_button(page):
            return "Could not open Progress Notes dialog"
        
        print("Progress Notes dialog should be open, extracting content...")
        page.wait_for_timeout(2000)
        
        # Take screenshot of opened Progress Notes
        if screenshot:
            print("Progress Notes dialog opened")
        
        # Step 2: Extract content from iframes
        clinical_content, success = extract_iframe_content(page, screenshot)
        
        if success and clinical_content:
            # Step 3: Parse the clinical content using NotesHandler
            try:
                from notes_handler import NotesHandler
                notes_handler = NotesHandler()
                parsed_notes = notes_handler.extract_clinical_notes_from_html(clinical_content)
                
                if parsed_notes and len(parsed_notes) > 100:
                    print("Successfully parsed clinical notes using NotesHandler")
                    clinical_notes = parsed_notes
                else:
                    print("NotesHandler parsing didn't yield sufficient content, using raw HTML")
                    clinical_notes = clinical_content
                    
            except Exception as parse_error:
                print(f"Error using NotesHandler: {parse_error}")
                clinical_notes = clinical_content
        else:
            clinical_notes = "No clinical notes could be extracted from ECW Progress Notes"
        
        # Step 4: Close Progress Notes dialog
        close_progress_notes_dialog(page)
        
        # Step 5: Display and save results
        if clinical_notes and len(clinical_notes) > 100:
            print("\n" + "=" * 60)
            print("EXTRACTED CLINICAL NOTES FROM ECW:")
            print("=" * 60)
            
            # Use NotesHandler to format and display the extracted notes
            try:
                from notes_handler import NotesHandler
                notes_handler = NotesHandler()
                formatted_notes = notes_handler.format_notes(clinical_notes)
                print(formatted_notes[:1500] + ("..." if len(formatted_notes) > 1500 else ""))
                print("=" * 60)
                print(f"Total notes length: {len(formatted_notes)} characters")
                
                # Save extracted notes to a file for review
                try:
                    with open('final_clinical_notes_for_bedrock.txt', 'w', encoding='utf-8') as f:
                        f.write("FINAL CLINICAL NOTES THAT WILL BE SENT TO BEDROCK\n")
                        f.write("=" * 80 + "\n")
                        f.write(f"Notes length: {len(formatted_notes)} characters\n")
                        f.write("=" * 80 + "\n\n")
                        f.write(formatted_notes)
                    print("Final clinical notes saved to 'final_clinical_notes_for_bedrock.txt' for review")
                except Exception as save_error:
                    print(f"Could not save final notes: {save_error}")
                
                return formatted_notes
                
            except Exception as format_error:
                print(f"Error formatting notes: {format_error}")
                return clinical_notes
        else:
            print("Failed to extract meaningful clinical notes")
            return "No clinical notes extracted"
        
    except Exception as e:
        print(f"Error during Progress Notes extraction: {e}")
        return f"Error extracting Progress Notes: {e}"