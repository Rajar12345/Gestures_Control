
import cv2
import mediapipe as mp
import pyautogui 
import time  

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

def calculate_distance(point1, point2):
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

def are_fingers_open(hand_landmarks, width, height):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    
    thumb_tip = (int(thumb_tip.x * width), int(thumb_tip.y * height))
    index_tip = (int(index_tip.x * width), int(index_tip.y * height))
    middle_tip = (int(middle_tip.x * width), int(middle_tip.y * height))
    ring_tip = (int(ring_tip.x * width), int(ring_tip.y * height))
    pinky_tip = (int(pinky_tip.x * width), int(pinky_tip.y * height))
    
    thumb_index = calculate_distance(thumb_tip, index_tip)
    index_middle = calculate_distance(index_tip, middle_tip)
    middle_ring = calculate_distance(middle_tip, ring_tip)
    ring_pinky = calculate_distance(ring_tip, pinky_tip)
    
    if thumb_index > 70 and index_middle > 70 and middle_ring > 70 and ring_pinky > 70:
        return True
    return False

# check if hand is in a fist (closed fist gesture)
def is_fist(hand_landmarks, width, height):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    
    thumb_tip = (int(thumb_tip.x * width), int(thumb_tip.y * height))
    index_tip = (int(index_tip.x * width), int(index_tip.y * height))
    middle_tip = (int(middle_tip.x * width), int(middle_tip.y * height))
    ring_tip = (int(ring_tip.x * width), int(ring_tip.y * height))
    pinky_tip = (int(pinky_tip.x * width), int(pinky_tip.y * height))
    
    thumb_index = calculate_distance(thumb_tip, index_tip)
    index_middle = calculate_distance(index_tip, middle_tip)
    middle_ring = calculate_distance(middle_tip, ring_tip)
    ring_pinky = calculate_distance(ring_tip, pinky_tip)
    
    if thumb_index < 30 and index_middle < 30 and middle_ring < 30 and ring_pinky < 30:
        return True
    return False

#  thumb and forefinger are together openai
def thumb_forefinger_together(hand_landmarks, width, height):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    
    thumb_tip = (int(thumb_tip.x * width), int(thumb_tip.y * height))
    index_tip = (int(index_tip.x * width), int(index_tip.y * height))
    
    distance = calculate_distance(thumb_tip, index_tip)
    
    if distance < 30:
        return True
    return False

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    result = hands.process(rgb_frame)
    
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # 5 fingers open maximized all windows
            if are_fingers_open(hand_landmarks, w, h):
                pyautogui.hotkey('win', 'd') 
                cv2.putText(frame, "Maximizing All Windows", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                time.sleep(0.1)  # Add a delay for smoother interaction
            
            #  closed fist minimize all windows
            elif is_fist(hand_landmarks, w, h):
                pyautogui.hotkey('win', 'd') 
                cv2.putText(frame, "Minimizing All Windows", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                time.sleep(0.1)  # Add a delay for smoother interaction
            
            # thumb and forefinger are together openai
            elif thumb_forefinger_together(hand_landmarks, w, h):
                pyautogui.hotkey('alt', 'space')
                cv2.putText(frame, "Alt+Space Triggered", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                time.sleep(0.1)  
            
            # index and middle fingers for scrolling
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            
            index_tip = (int(index_tip.x * w), int(index_tip.y * h))
            middle_tip = (int(middle_tip.x * w), int(middle_tip.y * h))
            
            distance = calculate_distance(index_tip, middle_tip)
            
            if distance < 40:   #FIngers are together
                pyautogui.scroll(30)  # Scroll up
                cv2.putText(frame, "Scrolling Up", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                time.sleep(0.1)  
            elif distance > 70:  # Fingers are far apart
                pyautogui.scroll(-30)  # Scroll down
                cv2.putText(frame, "Scrolling Down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                time.sleep(0.1) 
    
    cv2.imshow("Hand Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

cap.release()
cv2.destroyAllWindows()



