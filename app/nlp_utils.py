import spacy
import re

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

def extract_time(text):
    # Use a simpler approach to extract time
    time_pattern = re.compile(r'\b(\d{1,2}(?::\d{2})?\s*[ap]\.?m\.?)\b', re.IGNORECASE)
    matches = re.findall(time_pattern, text)
    if matches:
        return matches[0]
    return ""

def extract_information(note_text):
    # Extracted information
    extracted_info = {
        "Titles": [],    # Use a list for multiple titles
        "Dates": [],     # Use a list for multiple dates
        "Times": [],     # Use a list for multiple times
        "Locations": []  # Use a list for multiple locations
    }

    # Process the note with spaCy
    doc = nlp(note_text)

    # Extract date using regular expression
    date_pattern = re.compile(r'\b(\d{4}/\d{1,2}/\d{1,2})\b')
    date_matches = re.findall(date_pattern, note_text)

    # Search for the specific pattern "Event Name is [name]"
    for sent in doc.sents:
        for word in ["හෙට", "අනිද්දා"]:
            if word in sent.text:
                extracted_info["Dates"].append(word)

    # Add date matches to extracted_info["Dates"]
    for date_match in date_matches:
        extracted_info["Dates"].append(date_match)

    # Search for the specific pattern "Event Name is [name]"
    for sent in doc.sents:
        for word in ["මලගෙයක්", "දානයක්", "මගුල් ගෙයක්", "සාදයක්", "උපන් දින සාදයක්"]:
            if word in sent.text:
                extracted_info["Titles"].append(word)

    # Extract time using regular expression
    time_pattern = re.compile(r'\b(\d{1,2}(?:\.\d{1,2})?\s*[ap]\.?m\.?)\b', re.IGNORECASE)
    time_matches = re.findall(time_pattern, note_text)
    extracted_info["Times"] = time_matches

    # Extract locations
    for sent in doc.sents:
        for word in ["පානදුරේ", "බත්තරමුල්ලේ"]:
            if word in sent.text:
                extracted_info["Locations"].append(word)

    return extracted_info

def generate_reminder(extracted_info):
    reminder_template = ""

    for i in range(len(extracted_info["Titles"])):
        reminder_template += f"""
Reminder {i + 1}:
Title: {extracted_info["Titles"][i]}
Date: {extracted_info["Dates"][i]}
Time: {extracted_info["Times"][i]}
Location: {extracted_info["Locations"][i]}
        """

    return reminder_template

# Sample note
note_text = """
අද උදේ ස්කූල් ගියා.ගෙදර වැඩ දීලා තිබ්බ. ගණන් වලයි ගණන් විද්‍යාව වලයි  වලට.අන්ජන එක්ක අඩ යන්න තියනව cලස්ස් ෆී ගෙවන්න.ගෙඩර අවිල්ල කාම හඩල බල්ලව නවන්න තියන.ඊට 2024/11/23 පස්සෙ අම්ම cඅල්ල් කරල කිව්ව මලගෙයක් තියනව  යන්න ඔනෙ කියල 3.30 pm ට පානදුරේ .ඉට පස්සෙ අඩ රා කාල කලින් නිඩ ගන්න ඔනෙ.
අද උදේ ස්කූල් ගියා.ගෙදර වැඩ දීලා තිබ්බ. ගණන් වලයි ගණන් විද්‍යාව වලයි  වලට.අන්ජන එක්ක අඩ යන්න තියනව cලස්ස් ෆී ගෙවන්න.ගෙඩර අවිල්ල කාම හඩල බල්ලව නවන්න තියන.ඊට පස්සෙ අම්ම cඅල්ල් කරල කිව්ව සාදයක් තියනව හෙට යන්න ඔනෙ කියල 2.30 pm ට බත්තරමුල්ලේ .ඉට පස්සෙ අඩ රා කාල කලින් නිඩ ගන්න ඔනෙ.
"""

extracted_info = extract_information(note_text)
reminder = generate_reminder(extracted_info)
print(reminder)
