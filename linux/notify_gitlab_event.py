import subprocess


def notify_gitlab_event(description):
    # Play notification sound
    try:
        subprocess.Popen(["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"])
    except FileNotFoundError:
        # Fallback: try paplay or aplay, or skip sound if nothing works
        try:
            subprocess.Popen(["canberra-gtk-play", "--id", "message-new-instant"])
        except FileNotFoundError:
            try:
                subprocess.Popen(["aplay", "/usr/share/sounds/alsa/Front_Center.wav"])
            except FileNotFoundError:
                print("No sound player found for notification.")

    # Show desktop notification (title only)
    try:
        subprocess.Popen(["notify-send", "GitLab", description])
    except FileNotFoundError:
        print("notify-send is not installed or not available in this environment.")
