import numpy as np
import cv2

class Color:
    def __init__(self, lower, upper, border_color, menu):
        self.lower = lower
        self.upper = upper
        self.border_color = border_color
        self.menu = menu

    #for color mask
    def create_mask(self):
        kernel = np.ones((2, 2), "uint8")
        if self == red:
                mask1 = cv2.inRange(hsv_frame, self.lower, self.upper)
                mask2 = cv2.inRange(hsv_frame, np.array([173, 125, 125], np.uint8), np.array([180, 255, 255], np.uint8))

                mask = cv2.bitwise_or(mask1, mask2)
        else:
                mask = cv2.inRange(hsv_frame, self.lower, self.upper)
        return cv2.dilate(mask, kernel)

#class for menu items
class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

# a class for menus
class Menu:
    def __init__(self):
        self.item_list = {}

    # a method to add items
    def add_item(self, *sidenum_menuitem_pairs):
        for num_of_sides, menu_item in sidenum_menuitem_pairs:
            self.item_list[num_of_sides] = menu_item

    def __getitem__(self, num_of_sides):
        return self.item_list.get(num_of_sides)

    def __contains__(self, item):
        return item in tuple(self.item_list.values())

# Creating the menus categorized by their corresponding colors
# Red - Main Course
red_menu = Menu()
red_menu.add_item((3, MenuItem("Meatballs  110$", 110)),
                  (4, MenuItem("Casseroles  90$", 90)),
                  (5, MenuItem("Fajitas  75$", 75)))

# Green - Snacks
green_menu = Menu()
green_menu.add_item((3, MenuItem("Crispy Chicken  65$", 65)),
                    (4, MenuItem("Fish & Chips  70$", 70)),
                    (5, MenuItem("Omelet  45$", 45)))

# Blue - Starters
blue_menu = Menu()
blue_menu.add_item((3, MenuItem("Soup  55$", 55)),
                   (4, MenuItem("Cheese Platter  70$", 70)),
                   (5, MenuItem("Garlic Bread  40$", 40)))

# Yellow - Desserts
yellow_menu = Menu()
yellow_menu.add_item((3, MenuItem("Souffle  60$", 60)),
                     (4, MenuItem("Tiramisu  65$", 65)),
                     (5, MenuItem("Cheesecake  80$", 80)))

# A function to check the validity of an order
def order_validity(order):
    items = {"red": 0, "green": 0, "blue": 0, "yellow": 0}

    # Counting how many items of a menu are in the order
    for item in order:
        items["red"] += int(item in red_menu)
        items["green"] += int(item in green_menu)
        items["blue"] += int(item in blue_menu)
        items["yellow"] += int(item in yellow_menu)

    total_items = items["red"] + items["green"] + items["blue"] + items["yellow"]

    # Checking if there are more than one item from any menu
    if total_items > 4:
        print("You can only choose one item from every menu.")
        return False

    # Checking if there is at least one item in the order and if there is at least one item from main course and starter menus
    if items["red"] + items["blue"] < 2 or total_items < 1:
        print("You have to choose at least one main course and one starter menu item to order.")
        return False

    return True

red = Color(np.array([0, 125, 125], np.uint8), np.array([10, 255, 255], np.uint8), (0, 0, 255), red_menu)
green = Color(np.array([48, 111, 119], np.uint8), np.array([70, 255, 255], np.uint8), (0, 255, 0), green_menu)
blue = Color(np.array([104, 110, 102], np.uint8), np.array([130, 255, 255], np.uint8), (255, 0, 0), blue_menu)
yellow = Color(np.array([24, 106, 100], np.uint8), np.array([36, 255, 255], np.uint8), (0, 255, 255), yellow_menu)

color_bounds = (red, green, blue, yellow)

# Starting webcam video capture
webcam = cv2.VideoCapture(0)

print('Press "E" to confirm your order.')
while True:
    # Reading the captured frames from the webcam footage
    _, frame = webcam.read()

    # Converting the captured frame into HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Defining the variable for the frame of the webcam footage that is going to be displayed
    display_frame = frame.copy()

    # Defining an empty list for the order that will be detected
    detected_order = []

    # Iterating over every Color object
    for color_object in color_bounds:
        # Masking the color from the frame
        mask = color_object.create_mask()

        # Finding the contours that contain the color
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Making a tuple of contours filtered by area
        contours = tuple(contour for contour in contours if cv2.contourArea(contour) > 600)

        # Iterating over the filtered contours
        for contour in contours:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.03 * peri, True)

            # Generating the coordinate, width and height information for the current contour
            x, y, w, h = cv2.boundingRect(contour)

            # Making a check to see if the number of sides for the current contour correspond to any item in the current Color object's menu
            if color_object.menu[len(approx)] != None:
                # Drawing the bounding box for the current contour
                display_frame = cv2.rectangle(frame, (x, y),  (x + w, y + h),  color_object.border_color, 2)
                # Displaying the name of the menu item the current contour's number of sides correspond to
                cv2.putText(display_frame, color_object.menu[len(approx)].name, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_object.border_color)

                # Displaying the central coordinates of the bounding box
                cv2.putText(display_frame, f"({x + w//2},{y + h//2})", (x + w//2 - 40, y + 20 + h//2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
                # Marking the center of the bounding box
                display_frame = cv2.circle(display_frame, (x + w//2, y + h//2), 1, (0, 255, 255))

                # Adding the corresponding menu item to the order list
                detected_order.append(color_object.menu[len(approx)])
            else:
                pass

    # Displaying the processed image
    cv2.imshow("SENG - 211", display_frame)

    key = cv2.waitKey(1) & 0xFF

    # Assigning a key to exit the program
    if  key == ord("q"):
        break

    # Assigning a key to take a screenshot of the current order
    if key == ord("e"):
        # Checking the validity of the order
        if order_validity(detected_order):
            final_fee = 0

            print("Your order is:")

            # Calculating the total price for the order
            for item in detected_order:
                print(f'  -{item.name}: {item.price}TL')
                final_fee += item.price

            print(f"\nFinal fee: {final_fee}")

            # Prompting the user to confirm their order
            confirmation = bool(int(input('Confirm order with "1", cancel with "0": ')))

            if confirmation:
                print(f"Order confirmed. Enjoy your meal!")
            else:
                pass

# Releasing the webcam from the video capture
webcam.release()
cv2.destroyAllWindows()
