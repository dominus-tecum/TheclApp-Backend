import cv2
import numpy as np

# Known coin diameter in cm
COIN_DIAMETER_CM = 2.6

# Global variables
drawing = False
mode = 'coin'
start_point = (0, 0)
end_point = (0, 0)
coin_box = None
object_box = None
image = None
clone = None
zoom = 1.0
pan_x = 0
pan_y = 0
dragging = False
drag_start_x = 0
drag_start_y = 0
pan_start_x = 0
pan_start_y = 0

def mouse_callback(event, x, y, flags, param):
    global drawing, start_point, end_point, coin_box, object_box, image, clone, mode, dragging, drag_start_x, drag_start_y, pan_start_x, pan_start_y, pan_x, pan_y
    
    # Convert display coordinates to original
    orig_x = int((x - pan_x) / zoom)
    orig_y = int((y - pan_y) / zoom)
    
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (orig_x, orig_y)
        end_point = (orig_x, orig_y)
        
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_point = (orig_x, orig_y)
            redraw()
            x1 = int(min(start_point[0], end_point[0]) * zoom + pan_x)
            y1 = int(min(start_point[1], end_point[1]) * zoom + pan_y)
            x2 = int(max(start_point[0], end_point[0]) * zoom + pan_x)
            y2 = int(max(start_point[1], end_point[1]) * zoom + pan_y)
            if mode == 'coin':
                cv2.rectangle(display_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
            else:
                cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.imshow("Measurement Tool", display_image)
        elif dragging and (flags & cv2.EVENT_FLAG_RBUTTON):
            dx = x - drag_start_x
            dy = y - drag_start_y
            pan_x = pan_start_x + dx
            pan_y = pan_start_y + dy
            redraw()
            
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (orig_x, orig_y)
        x1 = min(start_point[0], end_point[0])
        y1 = min(start_point[1], end_point[1])
        x2 = max(start_point[0], end_point[0])
        y2 = max(start_point[1], end_point[1])
        width = x2 - x1
        height = y2 - y1
        if width > 5 and height > 5:
            if mode == 'coin':
                coin_box = (x1, y1, width, height)
                print(f"✅ Coin box: {width}x{height} pixels")
            else:
                object_box = (x1, y1, width, height)
                print(f"✅ Object box: {width}x{height} pixels")
            redraw()
            
    elif event == cv2.EVENT_RBUTTONDOWN:
        dragging = True
        drag_start_x = x
        drag_start_y = y
        pan_start_x = pan_x
        pan_start_y = pan_y
        
    elif event == cv2.EVENT_RBUTTONUP:
        dragging = False

def redraw():
    global display_image, image, zoom, pan_x, pan_y
    
    display_width = 900
    display_height = 700
    
    new_width = int(image.shape[1] * zoom)
    new_height = int(image.shape[0] * zoom)
    resized = cv2.resize(image, (new_width, new_height))
    
    display_image = np.zeros((display_height, display_width, 3), dtype=np.uint8)
    
    x_start = pan_x
    y_start = pan_y
    x_end = x_start + new_width
    y_end = y_start + new_height
    
    if x_start >= display_width or y_start >= display_height or x_end <= 0 or y_end <= 0:
        cv2.imshow("Measurement Tool", display_image)
        return
    
    img_x_start = max(0, -x_start)
    img_y_start = max(0, -y_start)
    img_x_end = min(new_width, display_width - x_start)
    img_y_end = min(new_height, display_height - y_start)
    
    disp_x_start = max(0, x_start)
    disp_y_start = max(0, y_start)
    
    display_image[disp_y_start:disp_y_start + (img_y_end - img_y_start), 
                  disp_x_start:disp_x_start + (img_x_end - img_x_start)] = \
        resized[img_y_start:img_y_end, img_x_start:img_x_end]
    
    # Draw saved boxes
    if coin_box:
        x1 = int(coin_box[0] * zoom + pan_x)
        y1 = int(coin_box[1] * zoom + pan_y)
        x2 = int((coin_box[0] + coin_box[2]) * zoom + pan_x)
        y2 = int((coin_box[1] + coin_box[3]) * zoom + pan_y)
        cv2.rectangle(display_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
    
    if object_box:
        x1 = int(object_box[0] * zoom + pan_x)
        y1 = int(object_box[1] * zoom + pan_y)
        x2 = int((object_box[0] + object_box[2]) * zoom + pan_x)
        y2 = int((object_box[1] + object_box[3]) * zoom + pan_y)
        cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
    
    cv2.imshow("Measurement Tool", display_image)

def calculate_length():
    global coin_box, object_box
    
    if coin_box is None:
        print("❌ Please draw coin box first")
        return
    if object_box is None:
        print("❌ Please draw object box first")
        return
    
    coin_pixels = max(coin_box[2], coin_box[3])
    object_pixels = max(object_box[2], object_box[3])
    pixels_per_cm = coin_pixels / COIN_DIAMETER_CM
    length_cm = object_pixels / pixels_per_cm
    
    print("\n" + "="*40)
    print(f"📏 MEASUREMENT RESULT")
    print("="*40)
    print(f"Coin diameter: {coin_pixels} pixels = {COIN_DIAMETER_CM} cm")
    print(f"Object length: {object_pixels} pixels")
    print(f"Pixels per cm: {pixels_per_cm:.2f}")
    print(f"📐 LENGTH: {length_cm:.1f} cm")
    print("="*40)

def zoom_in():
    global zoom, pan_x, pan_y
    zoom = min(zoom * 1.2, 10.0)
    redraw()
    print(f"🔍 Zoom: {zoom:.1f}x")

def zoom_out():
    global zoom, pan_x, pan_y
    zoom = max(zoom / 1.2, 0.2)
    redraw()
    print(f"🔍 Zoom: {zoom:.1f}x")

def main():
    global image, clone, mode, image_width, image_height
    
    image_path = input("Enter image path (or press Enter for c:\\temp\\test.jpg): ").strip('"')
    if not image_path:
        image_path = r"c:\temp\test.jpg"
    
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"❌ Could not load image from: {image_path}")
        return
    
    clone = image.copy()
    image_height, image_width = image.shape[:2]
    
    cv2.namedWindow("Measurement Tool")
    cv2.setMouseCallback("Measurement Tool", mouse_callback)
    redraw()
    
    print("\n" + "="*50)
    print("📏 MEASUREMENT TOOL")
    print("="*50)
    print("'+' or '=' key - Zoom IN")
    print("'-' key - Zoom OUT")
    print("RIGHT CLICK + DRAG - Pan (move view)")
    print("'c' - COIN mode (draw blue box)")
    print("'o' - OBJECT mode (draw red box)")
    print("'m' - Calculate length")
    print("'r' - Reset all")
    print("'q' - Quit")
    print("="*50 + "\n")
    print("🎯 MODE: COIN (draw blue box around the 2.6cm coin)")
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('c'):
            mode = 'coin'
            print("🎯 MODE: COIN - Draw blue box around the coin (2.6cm)")
        elif key == ord('o'):
            mode = 'object'
            print("🎯 MODE: OBJECT - Draw red box around the object")
        elif key == ord('+') or key == ord('='):
            zoom_in()
        elif key == ord('-'):
            zoom_out()
        elif key == ord('m'):
            calculate_length()
        elif key == ord('r'):
            coin_box = None
            object_box = None
            zoom = 1.0
            pan_x = 0
            pan_y = 0
            redraw()
            print("🔄 Reset all boxes and zoom")
        elif key == ord('q'):
            break
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()