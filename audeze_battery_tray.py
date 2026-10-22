import subprocess
import re
import pystray
from PIL import Image, ImageDraw, ImageFont
import threading
import time

# --- Configuration ---
CHECK_INTERVAL_SECONDS = 5 # Interval in seconds to check battery status at
HIDE_THRESHOLD_PERCENTAGE = 30 # Hide icon and trigger warning if below this value
SHOW_NOTIFICATION_PERCENTAGE = 20 # At how many percent a notification should be sent
TEXT_ON_FAIL = "?" # Text to show when we fail to fetch Battery Status

def exit_handler(icon, item):
    """Stops the tray icon and exits the script."""
    icon.stop()


class AudezeBatteryMonitor:
    def __init__(self):
        self.battery_level = TEXT_ON_FAIL
        self.is_low_battery = True
        self.has_sent_low_battery_warning = False

    def get_battery_status(self):
        """Runs headsetcontrol command and parses the output."""
        try:
            result = subprocess.run(
                ['headsetcontrol', '--battery'], 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if result.returncode != 0:
                print(f"Command failed with error: {result.stderr}")
                return TEXT_ON_FAIL

            # Parse "Level: XX%" from the output
            match = re.search(r'Level:\s*(\d+)%', result.stdout)
            if match:
                level = int(match.group(1))
                print(f"Battery Status fetched: {level}%")

                is_low = level <= SHOW_NOTIFICATION_PERCENTAGE

                if is_low and not self.has_sent_low_battery_warning:
                    self.show_notification(level)

                # Reset flag if battery recovers to high level
                if not is_low:
                    self.has_sent_low_battery_warning = False

                return level
            else:
                print("Could not parse battery level.")
                return TEXT_ON_FAIL

        except Exception as e:
            print(f"An error occurred checking battery: {e}")
            return TEXT_ON_FAIL

    def show_notification(self, level):
        try:
            # Send system notification with 'Critical' urgency
            subprocess.run(
                ['notify-send',
                    'Audeze Battery Low',
                    f'Battery dropped below {level}%. Please charge.',
                    '-u', 'critical'],
                capture_output=True, check=False
            )

            self.has_sent_low_battery_warning = True
        except Exception as e:
            print(f"Notification error (ensure libnotify-bin is installed): {e}")


    def update_icon(self, icon):
        """Called by the background thread to update the tray icon."""
        current_level = self.get_battery_status()

        if current_level == TEXT_ON_FAIL:
            icon.visible = False
            return

        # Did not change, don't update
        if self.battery_level == str(current_level) + "%":
            return

        self.battery_level = str(current_level) + "%"

        is_low = current_level < HIDE_THRESHOLD_PERCENTAGE
        
        # Note: In pystray/KDE, setting visible=False moves it to the overflow popup
        try:
            icon.visible = True
            img = self.create_icon_image(self.battery_level)
            icon.icon = img
            icon.tooltip = f"Audeze Battery: {self.battery_level}"

            # This is needed because the icon wont update if the icon is not visible
            time.sleep(0.001)
            icon.visible = is_low
        except Exception as e:
             print(f"Failed to update icon visual: {e}")


    def create_icon_image(self, text):
        """Generates an image with the percentage text."""
        width, height = 48, 24 # Icon size
        img = Image.new('RGBA', (width, height), color=(0, 0, 0, 0)) # Transparent background
        d = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 22)
        except:
            font = ImageFont.load_default()

        text_bbox = d.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Center the text
        x = (width - text_width) / 2
        y = (height - text_height) / 2
        
        d.text((x, y), text, fill=(255, 255, 255), font=font)
        return img


def main():
    monitor = AudezeBatteryMonitor()
    
    # Create the initial icon image (will show '?' until first check)
    img = monitor.create_icon_image(TEXT_ON_FAIL)

    context_menu = [pystray.MenuItem('Exit', exit_handler)]

    tray_icon = pystray.Icon(
        "Audeze_Battery", 
        img, 
        tooltip="Audeze Battery Monitor", 
        menu=context_menu
    )

    def start_update_loop(icon):
        while True:
            try:
                monitor.update_icon(icon)
            except Exception as e:
                print(f"Update loop error: {e}")

            time.sleep(CHECK_INTERVAL_SECONDS)

    t = threading.Thread(target=start_update_loop, args=(tray_icon,))
    t.daemon = True
    t.start()

    try:
        tray_icon.run()
    except KeyboardInterrupt:
        pass
    finally:
        print("Exiting battery monitor.")


if __name__ == "__main__":
    main()
