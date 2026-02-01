# -*- coding: utf-8 -*-
import cv2
import mediapipe as mp
from pynput.keyboard import Controller, Key
import time
import math
import numpy as np
import platform
import sys
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

AR_WORDS = []
EN_WORDS = []

def load_dictionary(path):
    import re
    words = set() 
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                parts = re.split(r'[،,]', line.strip())
                for w in parts:
                    clean_w = w.strip()
                    if clean_w:
                        words.add(clean_w)
        return sorted(list(words)) 
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return []

AR_WORDS = load_dictionary("D:/hand keyboard/arabic_words.txt")
EN_WORDS = load_dictionary("D:/hand keyboard/english_words.txt")

AR_WORDS.sort()
EN_WORDS.sort()


PILLOW_AVAILABLE = False
from PIL import Image, ImageDraw, ImageFont
PILLOW_AVAILABLE = True

RESHAPER_BIDI_AVAILABLE = False
import arabic_reshaper
from bidi.algorithm import get_display
RESHAPER_BIDI_AVAILABLE = True
print("arabic_reshaper and python-bidi imported successfully.")

SOUND_AVAILABLE = False
if platform.system() == "Windows":
    import winsound
    SOUND_AVAILABLE = True
    print("winsound imported successfully. Sound enabled.")
else:
    print("Sound disabled on non-Windows OS (winsound is Windows-only).")


ARABIC_FONT_PATH = "C:/Windows/Fonts/tahoma.ttf"
DEFAULT_FONT_PATH = "C:/Windows/Fonts/tahoma.ttf"
FALLBACK_FONT = cv2.FONT_HERSHEY_SIMPLEX 

FONT_SIZE_KEYS = 16      
FONT_SIZE_TEXT = 22      
FONT_SIZE_SUGGESTIONS = 16 

CLICK_MODE = 'PINCH'  
PINCH_DISTANCE_THRESHOLD = 30
DWELL_TIME_THRESHOLD = 0.5  
COOLDOWN_TIME = 0.3      
PROCESS_EVERY_N_FRAMES = 1 
HAND_MODEL_COMPLEXITY = 0  # 0 for faster, 1 for potentially more accurate

# -- Keyboard Layout & Appearance --
KEY_WIDTH_DEFAULT = 35  
KEY_HEIGHT = 35         
KEY_SPACING = 6          
KEYBOARD_START_X = 20
KEYBOARD_START_Y = 200    
KEY_BORDER_RADIUS = 8    
KEY_BORDER_THICKNESS = 1
KEY_TEXT_PADDING_X = 5
KEY_TEXT_PADDING_Y = 5

# -- Suggestions Appearance --
SUGGESTIONS_Y = 140 
SUGGESTIONS_HEIGHT = 35
SUGGESTIONS_SPACING = 10
SUGGESTIONS_PADDING_X = 10
SUGGESTIONS_PADDING_Y = 5
SUGGESTIONS_BORDER_RADIUS = 6
SUGGESTIONS_MAX = 5 

# -- Text Area Appearance --
TEXT_DISPLAY_Y = 70       
TEXT_DISPLAY_HEIGHT = 50  
TEXT_AREA_PADDING = 10    

# -- Colors (B, G, R) --
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_LIGHT_GREY = (215, 215, 215) 
COLOR_DARK_GREY = (130, 130, 130)
COLOR_KEY_TEXT = (40, 40, 40)     
COLOR_HIGHLIGHT = (180, 255, 180) 
COLOR_DWELL_HIGHLIGHT = (180, 255, 255) 
COLOR_CLICK = (255, 200, 200)     
COLOR_CAPS_ON = (255, 180, 100)  
COLOR_SHIFT_ON = (180, 220, 255)
COLOR_LANG_SWITCH = (150, 230, 230) 
COLOR_LEFT_FINGER = (255, 120, 0)
COLOR_RIGHT_FINGER = (0, 120, 255)
COLOR_THUMB = (0, 255, 255)
COLOR_PINCH_LINE = (255, 0, 255)
COLOR_TEXT_BG = (80, 80, 80)      
COLOR_TEXT_AREA_TEXT = COLOR_WHITE 
COLOR_SUGGESTION_BG = (160, 160, 160)
COLOR_SUGGESTION_BORDER = (100, 100, 100)
COLOR_SUGGESTION_TEXT = COLOR_WHITE
COLOR_SUGGESTION_HIGHLIGHT_BG = (190, 220, 190) 

# -- Sound --
USE_CLICK_SOUND = True
USE_HOVER_SOUND = False 
SOUND_CLICK_FREQ = 1600
SOUND_CLICK_DUR = 40
SOUND_HOVER_FREQ = 1000
SOUND_HOVER_DUR = 30



# --- Keyboard Layouts ---
KEY_ROWS_LOWER = [
    ['`','1','2','3','4','5','6','7','8','9','0','-','=','Bksp'],
    ['Tab','q','w','e','r','t','y','u','i','o','p','[',']','\\'],
    ['Caps','a','s','d','f','g','h','j','k','l',';','\'','Enter'],
    ['Shift','z','x','c','v','b','n','m',',','.','/','Shift'],
    [' ','AR','Space', '123',' ']
]
KEY_ROWS_UPPER = [
    ['~','!','@','#','$','%','^','&','*','(',')','_','+','Bksp'],
    ['Tab','Q','W','E','R','T','Y','U','I','O','P','{','}','|'],
    ['Caps','A','S','D','F','G','H','J','K','L',':','"','Enter'],
    ['Shift','Z','X','C','V','B','N','M','<','>','?','Shift'], 
    [' ','AR','Space', '123',' ']
]
KEY_ROWS_NUMSYM = [
    ['`','1','2','3','4','5','6','7','8','9','0','-','=','Bksp'],
    ['~','!','@','#','$','%','^','&','*','(',')','_','+','Tab'],
    ['{','}','|',':','"', '<','>','?', '[',']','\\',';','\'','Enter'],
    ['=','+','-','*','/',',','.','€','£','$','Shift'],
    [' ','ABC','Space','AR',' ']
]
KEY_ROWS_ARABIC = [
    ['ذ','١','٢','٣','٤','٥','٦','٧','٨','٩','٠','-','=','Bksp'], 
    ['ض','ص','ث','ق','ف','غ','ع','ه','خ','ح','ج','د','ش','\\'],
    ['Caps','ش','س','ي','ب','ل','ا','ت','ن','م','ك','ط','Enter'], 
    ['Shift','ئ','ء','ؤ','ر','لا','ى','ة','و','ز','ظ','ـ','Shift'], 
    [' ','EN','Space', '١٢٣',' ']
]
KEY_ROWS_ARABIC_NUMSYM = [ 
    ['`','1','2','3','4','5','6','7','8','9','0','-','=','Bksp'],
    ['~','!','@','#','$','%','^','&','*','(',')','_','+','Tab'],
    ['{','}','|',':','"', '<','>','?', '[',']','\\',';','\'','Enter'],
    ['=','+','-','*','/',',','.','€','£','$','Shift'], 
    [' ','ABC','Space','EN',' '] 
]

SPECIAL_WIDTHS = {
    'Bksp': int(KEY_WIDTH_DEFAULT * 1.6),
    'Tab': int(KEY_WIDTH_DEFAULT * 1.4),
    '\\': int(KEY_WIDTH_DEFAULT * 1.1),
    'Caps': int(KEY_WIDTH_DEFAULT * 1.5),
    'Enter': int(KEY_WIDTH_DEFAULT * 1.8),
    'Shift': int(KEY_WIDTH_DEFAULT * 2.0), 
    'Space': int(KEY_WIDTH_DEFAULT * 6.5 + KEY_SPACING * 5),
    ' ': int(KEY_WIDTH_DEFAULT * 2.5 + KEY_SPACING * 3.2),
    '123': int(KEY_WIDTH_DEFAULT * 1.3),
    'ABC': int(KEY_WIDTH_DEFAULT * 1.3),
    'AR': int(KEY_WIDTH_DEFAULT * 1.3),
    'EN': int(KEY_WIDTH_DEFAULT * 1.3),
    '١٢٣': int(KEY_WIDTH_DEFAULT * 1.3)
}


# --- Global Variables & Initializations ---
keyboard = Controller()
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(model_complexity=HAND_MODEL_COMPLEXITY,
                    max_num_hands=2,
                    min_detection_confidence=0.7, 
                    min_tracking_confidence=0.6) 
mp_draw = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles 

INDEX_FINGER_TIP_ID = mp_hands.HandLandmark.INDEX_FINGER_TIP.value
THUMB_TIP_ID = mp_hands.HandLandmark.THUMB_TIP.value

# --- Load Fonts ---
arabic_font = None
default_font = None
suggestions_font = None
text_area_font = None

if PILLOW_AVAILABLE:
    try:
        arabic_font = ImageFont.truetype(ARABIC_FONT_PATH, FONT_SIZE_KEYS)
        print(f"Arabic font loaded successfully from: {ARABIC_FONT_PATH}")
    except IOError:
        print(f"Error: Could not load Arabic font from: {ARABIC_FONT_PATH}. Pillow text drawing might fail.")
    try:
        default_font = ImageFont.truetype(DEFAULT_FONT_PATH, FONT_SIZE_KEYS)
        print(f"Default font loaded successfully from: {DEFAULT_FONT_PATH}")
    except IOError:
        print(f"Error: Could not load Default font from: {DEFAULT_FONT_PATH}.")

    try:
        suggestions_font = ImageFont.truetype(DEFAULT_FONT_PATH, FONT_SIZE_SUGGESTIONS)
    except IOError:
        print(f"Error loading font for suggestions. Using default keys font.")
        suggestions_font = default_font
    try:
        text_area_font = ImageFont.truetype(DEFAULT_FONT_PATH, FONT_SIZE_TEXT)
    except IOError:
        print(f"Error loading font for text area. Using default keys font.")
        text_area_font = default_font

# --- State Variables ---
key_layout_info = []
suggestion_layout_info = [] 
layout_calculated = False
caps_lock_on = False
shift_active = False
current_layout_mode = 'LOWER' 
typed_text = ""


was_pinching_left = False
was_pinching_right = False
dwell_target_info = None 
last_hovered_info_left = None 
last_hovered_info_right = None
last_pressed_info = None
click_feedback_info = {'type': None, 'info': None, 'time': 0}
frame_counter = 0
last_known_target_left = None 
last_known_target_right = None
pinch_line_left_coords = None 
pinch_line_right_coords = None

current_suggestions = []
last_suggestion_query_time = 0
suggestions_need_layout_update = False


# --- Helper Functions ---
def levenshtein_distance(a, b):
    if a == b:
        return 0
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)

    prev_row = list(range(len(b) + 1))

    for i, ca in enumerate(a, start=1):
        curr_row = [i]
        for j, cb in enumerate(b, start=1):
            insert_cost = curr_row[j - 1] + 1
            delete_cost = prev_row[j] + 1
            replace_cost = prev_row[j - 1] + (ca != cb)
            curr_row.append(min(insert_cost, delete_cost, replace_cost))
        prev_row = curr_row

    return prev_row[-1]

def normalize_arabic(word):
    replacements = {
        'أ':'ا', 'إ':'ا', 'آ':'ا',
        'ى':'ي', 'ة':'ه'
    }
    for k, v in replacements.items():
        word = word.replace(k, v)
    return word

def detect_language(word):
    if any('\u0600' <= c <= '\u06FF' for c in word):
        return "ar"
    if any('a' <= c <= 'z' or 'A' <= c <= 'Z' for c in word):
        return "en"
    return None

def get_local_suggestions(word_fragment):
    global current_suggestions, suggestions_need_layout_update

    if not isinstance(word_fragment, str) or not word_fragment.strip():
        current_suggestions = []
        suggestion_layout_info.clear()
        return

    lang = detect_language(word_fragment)
    fragment = word_fragment.strip().lower()
    word_list = AR_WORDS if lang == "ar" else EN_WORDS if lang == "en" else []
    
    new_suggestions_set = set()

    if lang == "ar":
        search_fragment = fragment[2:] if fragment.startswith("ال") else fragment
        search_fragment_norm = normalize_arabic(search_fragment)

        scored = []
        for word in word_list:
            w_clean = word[2:] if word.startswith("ال") else word
            w_norm = normalize_arabic(w_clean)

            dist = levenshtein_distance(search_fragment_norm, w_norm)
            
            if dist <= 1: 
                scored.append((dist, w_clean))
                scored.append((dist, "ال" + w_clean))

        scored.sort(key=lambda x: x[0])
        for _, w in scored:
            if len(new_suggestions_set) < SUGGESTIONS_MAX:
                new_suggestions_set.add(w)
            else:
                break
    else:
        scored = []
        for word in word_list:
            w_lower = word.lower()
            if abs(len(w_lower) - len(fragment)) <= 2:
                dist = levenshtein_distance(fragment, w_lower)
                if dist <= 2:
                    scored.append((dist, word))
        
        scored.sort(key=lambda x: x[0])
        for _, w in scored[:SUGGESTIONS_MAX]:
            new_suggestions_set.add(w)

    new_suggestions = list(new_suggestions_set)

    if new_suggestions != current_suggestions:
        current_suggestions = new_suggestions
        suggestion_layout_info.clear()
        suggestions_need_layout_update = True
        
def calculate_distance(p1, p2):
    """Calculates Euclidean distance between two 2D points."""
    try:
        if not isinstance(p1, (tuple, list)) or not isinstance(p2, (tuple, list)):
            return float('inf')
        if len(p1) < 2 or len(p2) < 2:
            return float('inf')
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])
    except TypeError: 
        return float('inf')
    except Exception: 
        return float('inf')


def play_sound(frequency, duration):
    """Plays a beep sound if winsound is available."""
    if SOUND_AVAILABLE and USE_CLICK_SOUND: 
        winsound.Beep(frequency, duration)

def play_click_sound():
    play_sound(SOUND_CLICK_FREQ, SOUND_CLICK_DUR)

def play_hover_sound():
    if USE_HOVER_SOUND:
        play_sound(SOUND_HOVER_FREQ, SOUND_HOVER_DUR)



def type_suggestion(suggestion_text):
    """Types the selected suggestion, replacing the current word fragment."""
    global typed_text, current_suggestions, suggestion_layout_info, suggestions_need_layout_update

    if not isinstance(suggestion_text, str) or not suggestion_text:
        return

    last_space_index = typed_text.rfind(' ')
    last_newline_index = typed_text.rfind('\n')
    start_index = max(last_space_index, last_newline_index) + 1
    word_fragment = typed_text[start_index:]

    text_to_type = ""
    if suggestion_text.startswith(word_fragment):
        text_to_type = suggestion_text[len(word_fragment):] + " "
    else:
        num_chars_to_delete = len(word_fragment)
        print(f"Replacing '{word_fragment}' with '{suggestion_text}'")
        for _ in range(num_chars_to_delete):
            keyboard.press(Key.backspace)
            keyboard.release(Key.backspace)
        text_to_type = suggestion_text + " "
        typed_text = typed_text[:start_index] 

    print(f"Typing suggestion part: '{text_to_type}'")
    keyboard.type(text_to_type)
    typed_text += text_to_type 

    current_suggestions = []
    suggestion_layout_info.clear()
    suggestions_need_layout_update = False 
    print("Suggestions cleared after selection.")


def press_element(element_info):

    global last_pressed_info, last_press_time, click_feedback_info
    global caps_lock_on, shift_active, current_layout_mode, typed_text
    global layout_calculated, current_suggestions, suggestion_layout_info, suggestions_need_layout_update

    if not element_info or 'type' not in element_info or 'info' not in element_info:
        print("Error: Invalid element_info passed to press_element")
        return

    element_type = element_info['type'] 
    info = element_info['info'] 
    current_time = time.time()

    is_same_element_instance = False
    last_info = last_pressed_info.get('info') if last_pressed_info else None

    if last_info and last_pressed_info.get('type') == element_type:
        if element_type == 'key' and info.get('key') == last_info.get('key'):
            is_same_element_instance = True
        elif element_type == 'suggestion' and info.get('text') == last_info.get('text'):
            is_same_element_instance = True

    if is_same_element_instance and (current_time - last_press_time < COOLDOWN_TIME):
        return 

    print(f"Processing press: Type='{element_type}', Info='{info.get('key') or info.get('text')}'")
    action_performed = False 
    text_changed = False     
    is_special_action = False 

    if element_type == 'suggestion':
        suggestion_text = info.get('text')
        if suggestion_text:
            type_suggestion(suggestion_text) 
            action_performed = True       

    elif element_type == 'key':
        key_value = info['key']
        key_to_press = None    
        char_to_type = None     
        original_key_value = key_value 

        if key_value == '123':
            current_layout_mode = 'NUMSYM'
            is_special_action = True; shift_active = False; layout_calculated = False
        elif key_value == 'ABC':
            current_layout_mode = 'UPPER' if caps_lock_on else 'LOWER'
            is_special_action = True; shift_active = False; layout_calculated = False
        elif key_value == 'AR':
            current_layout_mode = 'ARABIC'
            is_special_action = True; shift_active = False; caps_lock_on = False; layout_calculated = False
        elif key_value == 'EN':
            current_layout_mode = 'LOWER'
            is_special_action = True; shift_active = False; caps_lock_on = False; layout_calculated = False
        elif key_value == '١٢٣':
            current_layout_mode = 'NUMSYM' 
            is_special_action = True; shift_active = False; caps_lock_on = False; layout_calculated = False
        elif key_value == 'Caps':
            caps_lock_on = not caps_lock_on
            if current_layout_mode in ['LOWER', 'UPPER']:
                current_layout_mode = 'UPPER' if caps_lock_on else 'LOWER'
                layout_calculated = False 
            is_special_action = True
            print(f"Caps Lock {'ON' if caps_lock_on else 'OFF'}")
        elif key_value == 'Shift':
            shift_active = not shift_active 
            is_special_action = True
            print(f"Shift Active: {shift_active}")

        else:
            is_typing_key = True 
            temp_shift_active = shift_active 

            if key_value == 'Space': key_to_press, char_to_type = Key.space, " "
            elif key_value == 'Enter': key_to_press, char_to_type = Key.enter, "\n"
            elif key_value == 'Bksp': key_to_press = Key.backspace
            elif key_value == 'Tab': key_to_press, char_to_type = Key.tab, "\t"
            elif isinstance(key_value, str) and len(key_value) == 1:
                char_to_type = key_value 
            elif key_value in ['\\', '[', ']', '{', '}', '|', ';', ':', "'", '"', ',', '<', '.', '>', '/', '?', '~', '`', '-', '_', '=', '+']:
                char_to_type = key_value 
            else:
                print(f"Warning: Unhandled key value during typing: {key_value} (Type: {type(key_value)})")
                is_typing_key = False

            if is_typing_key and temp_shift_active and key_to_press not in [Key.backspace, Key.enter, Key.tab, Key.space]:
                print(f"Applying Shift to '{original_key_value}'...")
                source_rows, target_rows = None, None
                if current_layout_mode == 'LOWER': source_rows, target_rows = KEY_ROWS_LOWER, KEY_ROWS_UPPER
                elif current_layout_mode == 'UPPER': source_rows, target_rows = KEY_ROWS_UPPER, KEY_ROWS_LOWER
                elif current_layout_mode == 'NUMSYM':
                    shift_map_numsym = {'1':'!', '2':'@', '3':'#', '4':'$', '5':'%', '6':'^', '7':'&', '8':'*', '9':'(', '0':')', '-':'_', '=':'+',
                                        '`':'~', '[':'{', ']':'}', '\\':'|', ';':':', "'":'"', ',':'<', '.':'>', '/':'?'} 
                    char_to_type = shift_map_numsym.get(original_key_value, char_to_type) 
                    key_to_press = None 
                elif current_layout_mode == 'ARABIC':
                    pass 

                shifted_char = None
                if source_rows and target_rows:
                    found = False
                    for r_idx, row in enumerate(source_rows):
                        try:
                            c_idx = row.index(original_key_value)
                            if r_idx < len(target_rows) and c_idx < len(target_rows[r_idx]):
                                potential_shifted = target_rows[r_idx][c_idx]
                                if isinstance(potential_shifted, str) and len(potential_shifted) == 1:
                                    shifted_char = potential_shifted
                                    print(f"Shift result from layout mapping: Found shifted char '{shifted_char}'")
                                else:
                                    print(f"Shift mapping for '{original_key_value}' resulted in non-typeable key '{potential_shifted}'.")
                            else:
                                print(f"Shift mapping index out of bounds for '{original_key_value}'.")
                            found = True
                            break 
                        except ValueError:
                            continue 
                    if found and shifted_char:
                        char_to_type = shifted_char
                        key_to_press = None 
                    elif found and not shifted_char:

                        pass 
                    elif not found:
                        print(f"Could not find '{original_key_value}' in source layout '{current_layout_mode}' for Shift mapping.")

                shift_active = False
                print("Shift deactivated after use.")

            if key_to_press == Key.backspace:
                if len(typed_text) > 0:
                    typed_text = typed_text[:-1] 
                    text_changed = True 
                keyboard.press(key_to_press) 
                keyboard.release(key_to_press) 
                action_performed = True 
                print("Pressed Backspace")
            elif key_to_press and char_to_type:
                typed_text += char_to_type 
                text_changed = True 
                keyboard.press(key_to_press) 
                keyboard.release(key_to_press) 
                action_performed = True 
                print(f"Pressed Special Key: {original_key_value}")
            elif char_to_type:
                typed_text += char_to_type 
                text_changed = True 
                keyboard.type(char_to_type) 
                action_performed = True 
                print(f"Typed Char: {char_to_type}")
    if action_performed or is_special_action:
        last_pressed_info = {'type': element_type, 'info': info, 'time': current_time}
        last_press_time = current_time
        click_feedback_info = {'type': element_type, 'info': info, 'time': current_time}
        play_click_sound()

        if element_type == 'key':
            key_value = info['key'] 
            if text_changed and key_value != 'Bksp':
                current_word_fragment = ""
                if typed_text and not typed_text[-1].isspace() and typed_text[-1] != '\n':
                    last_space_index = typed_text.rfind(' ')
                    last_newline_index = typed_text.rfind('\n')
                    start_index = max(last_space_index, last_newline_index) + 1
                    current_word_fragment = typed_text[start_index:] 

                if current_word_fragment:
                    get_local_suggestions(current_word_fragment)
                else:
                    if current_suggestions:
                        current_suggestions = []
                        suggestion_layout_info.clear()
                        suggestions_need_layout_update = False

            elif key_value == 'Bksp' or key_value == 'Space':
                if current_suggestions: 
                    print(f"Clearing suggestions (due to {key_value}).")
                    current_suggestions = []
                    suggestion_layout_info.clear() 
                    suggestions_need_layout_update = False 

def calculate_key_layout(frame_width, frame_height):
    """Calculates the position and size of each key with pre-processed Arabic labels for performance."""
    global layout_calculated, key_layout_info, current_layout_mode

    if not frame_width or not frame_height: return
    print(f"Calculating key layout for mode: {current_layout_mode}")
    key_layout_info.clear() 
    start_x = KEYBOARD_START_X
    current_y = KEYBOARD_START_Y

    display_rows = []
    if current_layout_mode == 'LOWER': display_rows = KEY_ROWS_LOWER
    elif current_layout_mode == 'UPPER': display_rows = KEY_ROWS_UPPER
    elif current_layout_mode == 'NUMSYM': display_rows = KEY_ROWS_NUMSYM
    elif current_layout_mode == 'ARABIC': display_rows = KEY_ROWS_ARABIC
    elif current_layout_mode == 'ARABIC_NUMSYM': display_rows = KEY_ROWS_ARABIC_NUMSYM
    else: display_rows = KEY_ROWS_LOWER 
    
    base_layout_for_width = KEY_ROWS_LOWER
    if current_layout_mode in ['ARABIC']: base_layout_for_width = KEY_ROWS_ARABIC
    elif current_layout_mode in ['NUMSYM', 'ARABIC_NUMSYM']: base_layout_for_width = KEY_ROWS_NUMSYM

    for row_index, display_row in enumerate(display_rows):
        current_x = start_x
        for key_index, key_value_to_display in enumerate(display_row):
            base_key_name_for_width = key_value_to_display
            if key_value_to_display not in SPECIAL_WIDTHS and \
               row_index < len(base_layout_for_width) and \
               key_index < len(base_layout_for_width[row_index]):
                potential_base_name = base_layout_for_width[row_index][key_index]
                if potential_base_name in SPECIAL_WIDTHS:
                    base_key_name_for_width = potential_base_name

            key_width = SPECIAL_WIDTHS.get(base_key_name_for_width, KEY_WIDTH_DEFAULT)
            x1, y1 = current_x, current_y
            x2, y2 = current_x + int(key_width), current_y + KEY_HEIGHT

            # --- التعديل الجوهري للسرعة ---
            display_label = key_value_to_display
            is_arabic_char = False
            
            if isinstance(key_value_to_display, str):
                is_arabic_char = any('\u0600' <= char <= '\u06FF' for char in key_value_to_display)
                
                # إذا كان حرفاً عربياً، نقوم بعمل الـ Reshape والـ Bidi هنا "مرة واحدة فقط"
                if is_arabic_char and RESHAPER_BIDI_AVAILABLE:
                    reshaped = arabic_reshaper.reshape(key_value_to_display)
                    display_label = get_display(reshaped)

            key_layout_info.append({
                'key': key_value_to_display, 
                'display_label': display_label, # النص الجاهز للرسم فوراً
                'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                'base_name': base_key_name_for_width, 
                'is_arabic': is_arabic_char
            })
            # ------------------------------
            
            current_x += int(key_width) + KEY_SPACING
        current_y += KEY_HEIGHT + KEY_SPACING

    print(f"Key layout calculation complete. {len(key_layout_info)} keys positioned.")
    layout_calculated = True

def calculate_suggestion_layout(frame_width):
    global suggestion_layout_info, suggestions_need_layout_update
    if not current_suggestions or not suggestions_need_layout_update: return 

    suggestion_layout_info.clear()
    current_x = KEYBOARD_START_X
    y1, y2 = SUGGESTIONS_Y, SUGGESTIONS_Y + SUGGESTIONS_HEIGHT

    for suggestion_text in current_suggestions:
        if not suggestion_text: continue
        
        is_ar = any('\u0600' <= char <= '\u06FF' for char in suggestion_text)
        display_text = suggestion_text
        if is_ar and RESHAPER_BIDI_AVAILABLE:
            display_text = get_display(arabic_reshaper.reshape(suggestion_text))
        
        bbox = suggestions_font.getbbox(display_text) if PILLOW_AVAILABLE else [0,0,len(display_text)*10,0]
        text_width = int((bbox[2] - bbox[0]) + SUGGESTIONS_PADDING_X * 2)
        
        if current_x + text_width > frame_width - KEYBOARD_START_X: break

        suggestion_layout_info.append({
            'text': suggestion_text,
            'display_text': display_text, 
            'x1': current_x, 'y1': y1, 'x2': current_x + text_width, 'y2': y2,
            'is_arabic': is_ar 
        })
        current_x += text_width + SUGGESTIONS_SPACING
    suggestions_need_layout_update = False

def find_target(finger_coords_px, key_layout, suggestion_layout):
    """Finds which element (key or suggestion) the finger is pointing at."""
    if not finger_coords_px: return None
    fx, fy = finger_coords_px

    for sug_info in suggestion_layout:
        if sug_info['x1'] <= fx <= sug_info['x2'] and \
           sug_info['y1'] <= fy <= sug_info['y2']:
            return {'type': 'suggestion', 'info': sug_info}

    for key_info in key_layout:
        if key_info['x1'] <= fx <= key_info['x2'] and \
           key_info['y1'] <= fy <= key_info['y2']:
            return {'type': 'key', 'info': key_info}

    return None 
def draw_rounded_rectangle_pillow(draw, xy, radius, fill=None, outline=None, width=1):
    """ Helper to draw rounded rectangle using Pillow. xy is ((x1,y1), (x2,y2)) """
    x1, y1 = xy[0]
    x2, y2 = xy[1]
    draw.rounded_rectangle(xy=((x1,y1),(x2,y2)), radius=radius, fill=fill, outline=outline, width=width)


def draw_element_pillow(draw, element_info, bg_color, text_color, font, border_color, border_radius, is_suggestion=False):
    x1, y1, x2, y2 = element_info['x1'], element_info['y1'], element_info['x2'], element_info['y2']
    
    processed_text = element_info.get('display_label') or element_info.get('display_text') or \
                     str(element_info.get('key') or element_info.get('text', ''))
    
    draw_rounded_rectangle_pillow(draw, ((x1, y1), (x2, y2)), border_radius, fill=bg_color, outline=border_color, width=KEY_BORDER_THICKNESS)

    if processed_text and font:
        bbox = draw.textbbox((0, 0), processed_text, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = x1 + ( (x2-x1) - text_w) / 2 - bbox[0]
        ty = y1 + ( (y2-y1) - text_h) / 2 - bbox[1]
        draw.text((tx, ty), processed_text, font=font, fill=tuple(reversed(text_color)))
        

def draw_element_cv(frame, element_info, bg_color, text_color, border_color):
    """Fallback drawing using only OpenCV (lower quality text)."""
    x1, y1, x2, y2 = element_info['x1'], element_info['y1'], element_info['x2'], element_info['y2']
    text = str(element_info.get('key') or element_info.get('text', ''))
    w, h = x2 - x1, y2 - y1

    cv2.rectangle(frame, (x1, y1), (x2, y2), bg_color, cv2.FILLED)
    cv2.rectangle(frame, (x1, y1), (x2, y2), border_color, KEY_BORDER_THICKNESS)

    if text:
        font_scale = 0.6 if len(text) > 1 else 0.7
        thickness = 1
        text_size, _ = cv2.getTextSize(text, FALLBACK_FONT, font_scale, thickness)
        text_x = x1 + (w - text_size[0]) // 2
        text_y = y1 + (h + text_size[1]) // 2
        cv2.putText(frame, text, (text_x, text_y), FALLBACK_FONT, font_scale, text_color, thickness, lineType=cv2.LINE_AA)

    return frame


def draw_keyboard_and_suggestions(frame, targeted_left_info, targeted_right_info, dwell_info):
    """Draws the virtual keyboard and suggestions using Pillow if available."""
    global click_feedback_info, caps_lock_on, shift_active, current_layout_mode
    current_time = time.time()
    frame_height, frame_width, _ = frame.shape

    pil_im = None
    draw = None
    if PILLOW_AVAILABLE and default_font: 
        frame_copy = np.ascontiguousarray(frame)
        pil_im = Image.fromarray(cv2.cvtColor(frame_copy, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_im)
    else:
        pass 

    if click_feedback_info['type'] and (current_time - click_feedback_info['time'] > 0.2): 
        click_feedback_info = {'type': None, 'info': None, 'time': 0}

    if suggestion_layout_info:
        for sug_info in suggestion_layout_info:
            bg_color = COLOR_SUGGESTION_BG
            text_color = COLOR_SUGGESTION_TEXT
            border_color = COLOR_SUGGESTION_BORDER

            is_targeted = (targeted_left_info and targeted_left_info['type'] == 'suggestion' and targeted_left_info['info'] == sug_info) or \
                        (targeted_right_info and targeted_right_info['type'] == 'suggestion' and targeted_right_info['info'] == sug_info)
            is_dwell = dwell_info and dwell_info['type'] == 'suggestion' and dwell_info['info'] == sug_info
            is_click = click_feedback_info['type'] == 'suggestion' and click_feedback_info['info'] == sug_info

            if is_targeted: bg_color = COLOR_SUGGESTION_HIGHLIGHT_BG
            if CLICK_MODE == 'DWELL' and is_dwell: bg_color = COLOR_DWELL_HIGHLIGHT 
            if is_click: bg_color = COLOR_CLICK

            if draw:
                draw_element_pillow(draw, sug_info, tuple(reversed(bg_color)), tuple(reversed(text_color)), suggestions_font, tuple(reversed(border_color)), SUGGESTIONS_BORDER_RADIUS, is_suggestion=True)
            else:
                frame = draw_element_cv(frame, sug_info, bg_color, text_color, border_color)

    if not layout_calculated or not key_layout_info:
        if pil_im:
            frame = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
        return frame

    for key_info in key_layout_info:
        key_value = key_info['key']
        bg_color = COLOR_LIGHT_GREY
        text_color = COLOR_KEY_TEXT
        border_color = COLOR_DARK_GREY

        is_targeted_left = targeted_left_info and targeted_left_info['type'] == 'key' and targeted_left_info['info'] == key_info
        is_targeted_right = targeted_right_info and targeted_right_info['type'] == 'key' and targeted_right_info['info'] == key_info
        is_dwell_key = dwell_info and dwell_info['type'] == 'key' and dwell_info['info'] == key_info
        is_click_key = click_feedback_info['type'] == 'key' and click_feedback_info['info'] == key_info

        if is_click_key:
            bg_color = COLOR_CLICK
        elif CLICK_MODE == 'DWELL' and is_dwell_key:
            bg_color = COLOR_DWELL_HIGHLIGHT
        elif is_targeted_left or is_targeted_right:
            bg_color = COLOR_HIGHLIGHT
        elif key_value == 'Caps' and caps_lock_on:
            bg_color = COLOR_CAPS_ON
            text_color = COLOR_WHITE 
        elif key_value == 'Shift' and shift_active:
            bg_color = COLOR_SHIFT_ON
            text_color = COLOR_BLACK 
        elif key_value in ['AR', 'EN', '123', 'ABC', '١٢٣']:
            bg_color = COLOR_LANG_SWITCH
            text_color = COLOR_WHITE

        current_key_font = default_font
        if key_info.get('is_arabic') and arabic_font:
            current_key_font = arabic_font

        if draw and current_key_font: 
            draw_element_pillow(draw, key_info, tuple(reversed(bg_color)), tuple(reversed(text_color)), current_key_font, tuple(reversed(border_color)), KEY_BORDER_RADIUS, is_suggestion=False)
        else:             frame = draw_element_cv(frame, key_info, bg_color, text_color, border_color)


    if pil_im:
        frame = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)

    return frame


def draw_typed_text(frame):
    """Draws the accumulated typed text with background and Pillow rendering."""
    frame_height, frame_width, _ = frame.shape
    if frame_width <= 0: return frame

    bg_x1 = KEYBOARD_START_X
    bg_y1 = TEXT_DISPLAY_Y - TEXT_DISPLAY_HEIGHT + 5
    bg_x2 = frame_width - KEYBOARD_START_X
    bg_y2 = TEXT_DISPLAY_Y + 10
    cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), COLOR_TEXT_BG, cv2.FILLED)
    cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), COLOR_DARK_GREY, 1)

    display_text = typed_text.replace("\t", "    ") 

    if PILLOW_AVAILABLE and text_area_font:
        text_area_slice = frame[bg_y1:bg_y2, bg_x1:bg_x2]
        text_area_slice = np.ascontiguousarray(text_area_slice)
        pil_im_text = Image.fromarray(cv2.cvtColor(text_area_slice, cv2.COLOR_BGR2RGB))
        draw_text = ImageDraw.Draw(pil_im_text)

        processed_text = display_text
        if RESHAPER_BIDI_AVAILABLE:
            reshaped_text = arabic_reshaper.reshape(display_text)
            processed_text = get_display(reshaped_text)
        elif any('\u0600' <= char <= '\u06FF' for char in display_text):
                processed_text = display_text[::-1] 

        available_width = bg_x2 - bg_x1 - (TEXT_AREA_PADDING * 2)
        text_width = 0
        bbox = draw_text.textbbox((0,0), processed_text, font=text_area_font)
        text_width = bbox[2] - bbox[0]

        if text_width > available_width:
            avg_char_width = text_width / len(processed_text) if len(processed_text) > 0 else 10
            max_chars = int(available_width / avg_char_width)
            processed_text = processed_text[:max_chars-3] + "..."

        bbox = draw_text.textbbox((0,0), processed_text, font=text_area_font)
        final_text_width = bbox[2] - bbox[0]
        final_text_height = bbox[3] - bbox[1]

        text_x = TEXT_AREA_PADDING 
        area_height = bg_y2 - bg_y1
        text_y = (area_height - final_text_height) // 2 - bbox[1] 
        draw_text.text((text_x, text_y), processed_text, font=text_area_font, fill=tuple(reversed(COLOR_TEXT_AREA_TEXT)))
        processed_slice_bgr = cv2.cvtColor(np.array(pil_im_text), cv2.COLOR_RGB2BGR)
        frame[bg_y1:bg_y2, bg_x1:bg_x2] = processed_slice_bgr

    else:
        cv2.putText(frame, display_text[-30:], 
                    (bg_x1 + TEXT_AREA_PADDING, bg_y2 - TEXT_AREA_PADDING), 
                    FALLBACK_FONT, 0.7, COLOR_TEXT_AREA_TEXT, 1, cv2.LINE_AA)

    return frame

def draw_landmarks_and_lines(frame, hand_landmarks, hand_label, is_pinching, pinch_line_coords):
    """Draws hand landmarks and the pinch line."""
    mp_draw.draw_landmarks(
        frame,
        hand_landmarks,
        mp_hands.HAND_CONNECTIONS,
        mp_drawing_styles.get_default_hand_landmarks_style(),
        mp_drawing_styles.get_default_hand_connections_style())

    if is_pinching and pinch_line_coords:
        p1, p2 = pinch_line_coords
        cv2.line(frame, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), COLOR_PINCH_LINE, 2)


cap = cv2.VideoCapture(0)

print("\nStarting Virtual Keyboard...")
print("Press 'Esc' or 'q' to exit.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    frame_counter += 1
    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape

    if not layout_calculated:
        calculate_key_layout(frame_width, frame_height)
    if suggestions_need_layout_update:
        calculate_suggestion_layout(frame_width)

    process_this_frame = (frame_counter % PROCESS_EVERY_N_FRAMES == 0)

    hand_coords = {'Left': {}, 'Right': {}} 
    results = None 
    frame.flags.writeable = False
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    frame.flags.writeable = True

    is_pinching_left_now = False
    is_pinching_right_now = False
    pinch_line_left_coords = None
    pinch_line_right_coords = None
    current_target_left = None
    current_target_right = None

    if results and results.multi_hand_landmarks:
        for hand_index, hand_landmarks in enumerate(results.multi_hand_landmarks):
            hand_label = 'Unknown'
            if results.multi_handedness and len(results.multi_handedness) > hand_index:
                hand_label = results.multi_handedness[hand_index].classification[0].label

            coords_for_hand = {}
            for id, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * frame_width), int(lm.y * frame_height)
                coords_for_hand[id] = (cx, cy)

            if hand_label in ['Left', 'Right']:
                hand_coords[hand_label] = coords_for_hand

            index_tip_px = coords_for_hand.get(INDEX_FINGER_TIP_ID)
            thumb_tip_px = coords_for_hand.get(THUMB_TIP_ID)

            if index_tip_px and thumb_tip_px:
                distance = calculate_distance(index_tip_px, thumb_tip_px)
                is_pinching_now = distance < PINCH_DISTANCE_THRESHOLD

                target_info = find_target(index_tip_px, key_layout_info, suggestion_layout_info)

                if hand_label == 'Left':
                    is_pinching_left_now = is_pinching_now
                    if is_pinching_left_now:
                        pinch_line_left_coords = (index_tip_px, thumb_tip_px)
                    current_target_left = target_info
                    if CLICK_MODE == 'PINCH' and is_pinching_left_now and not was_pinching_left:
                        print(f"PINCH START - Left - Target: {target_info['info'].get('key') if target_info else 'None'}")
                        press_element(target_info)

                    if CLICK_MODE == 'DWELL':
                        if target_info: 
                            if dwell_target_info and dwell_target_info['info'] == target_info['info'] and dwell_target_info['hand'] == 'Left':
                                dwell_duration = time.time() - dwell_target_info['start_time']
                                if dwell_duration > DWELL_TIME_THRESHOLD:
                                    print(f"DWELL COMPLETE - Left - Target: {target_info['info'].get('key') if target_info else 'None'}")
                                    press_element(target_info)
                                    dwell_target_info = None
                            else:
                                print(f"Dwell START - Left - Target: {target_info['info'].get('key') if target_info else 'None'}")
                                dwell_target_info = {'type': target_info['type'], 'info': target_info['info'], 'start_time': time.time(), 'hand': 'Left'}
                                play_hover_sound() 
                        elif dwell_target_info and dwell_target_info['hand'] == 'Left':
                            dwell_target_info = None

                elif hand_label == 'Right':
                    is_pinching_right_now = is_pinching_now
                    if is_pinching_right_now:
                        pinch_line_right_coords = (index_tip_px, thumb_tip_px)
                    current_target_right = target_info
                    if CLICK_MODE == 'PINCH' and is_pinching_right_now and not was_pinching_right:
                        print(f"PINCH START - Right - Target: {target_info['info'].get('key') if target_info else 'None'}")
                        press_element(target_info)

                    if CLICK_MODE == 'DWELL':
                        if target_info: 
                            if dwell_target_info and dwell_target_info['info'] == target_info['info'] and dwell_target_info['hand'] == 'Right':
                                dwell_duration = time.time() - dwell_target_info['start_time']
                                if dwell_duration > DWELL_TIME_THRESHOLD:
                                    print(f"DWELL COMPLETE - Right - Target: {target_info['info'].get('key') if target_info else 'None'}")
                                    press_element(target_info)
                                    dwell_target_info = None
                            else:
                                print(f"Dwell START - Right - Target: {target_info['info'].get('key') if target_info else 'None'}")
                                dwell_target_info = {'type': target_info['type'], 'info': target_info['info'], 'start_time': time.time(), 'hand': 'Right'}
                                play_hover_sound()
                        elif dwell_target_info and dwell_target_info['hand'] == 'Right':
                            dwell_target_info = None

    was_pinching_left = is_pinching_left_now
    was_pinching_right = is_pinching_right_now
    last_known_target_left = current_target_left
    last_known_target_right = current_target_right

    if dwell_target_info:
        hand_label_dwelling = dwell_target_info.get('hand')
        if hand_label_dwelling not in hand_coords or not hand_coords[hand_label_dwelling]:
            dwell_target_info = None

    frame = draw_typed_text(frame)

    frame = draw_keyboard_and_suggestions(frame, last_known_target_left, last_known_target_right, dwell_target_info)

    if results and results.multi_hand_landmarks:
        if 'Left' in hand_coords and hand_coords['Left']:
            left_hand_lms = None
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                if results.multi_handedness[i].classification[0].label == 'Left':
                    left_hand_lms = hand_landmarks
                    break
            if left_hand_lms:
                draw_landmarks_and_lines(frame, left_hand_lms, 'Left', is_pinching_left_now, pinch_line_left_coords)

        if 'Right' in hand_coords and hand_coords['Right']:
            right_hand_lms = None
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                if results.multi_handedness[i].classification[0].label == 'Right':
                    right_hand_lms = hand_landmarks
                    break
            if right_hand_lms:
                draw_landmarks_and_lines(frame, right_hand_lms, 'Right', is_pinching_right_now, pinch_line_right_coords)

    cv2.imshow('Virtual Keyboard - Press Esc/q to Exit', frame)

    key = cv2.waitKey(5) & 0xFF
    if key == 27 or key == ord('q'): 
        break

print("Exiting...")
cap.release()
cv2.destroyAllWindows()
print("Resources released.")
