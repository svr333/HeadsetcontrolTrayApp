# Headsetcontrol Tray App
Small app with inspiration from [This Repo](https://github.com/DByte308/audeze-maxwell-battery) for a small KDE Plasma Tray icon that shows the battery of any headset compatible with [Headsetcontrol](https://github.com/Sapd/HeadsetControl).

The app does the following:
- Notification at a configurable percentage
- Generate icon with battery percentage, only show if it meets configurable threshold

I am content with my version, however further improvements are possible:
- Different text color based on battery percentage
- Context menu actions to manually refresh percentage
- Use headset name received from command instead of generic name
- and probably many more...

## Requirements
- [Headsetcontrol](https://github.com/Sapd/HeadsetControl)
- Python, Python-Pillow
- notify-send if you want to send notifications

This app was made with qwen3.6-27B.
