import logging
import os
from app import app

# Suppress verbose Flask traffic logs to keep terminal clean
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

print("\n" + "="*60)
print("[WEB STUDIO INITIATED]")
print("Click the link below (CTRL+Click) to open the interactive website for deeper modifications!")
print("  http://127.0.0.1:5001")
print("="*60 + "\n")

if __name__ == '__main__':
    import socket

    def find_available_port(default_port=5001):
        if "PORT" in os.environ:
            return int(os.environ["PORT"])
        for p in [default_port, 5003, 5004, 5005]:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', p))
                    return p
            except OSError:
                continue
        return default_port

    port = find_available_port(5001)
    tracker = None
    if os.environ.get("USE_CODECARBON") == "1":
        try:
            from codecarbon import EmissionsTracker
        except ImportError as error:
            raise RuntimeError(
                "USE_CODECARBON=1 requires CodeCarbon in the active Python environment."
            ) from error

        tracker = EmissionsTracker(save_to_file=True, log_level='error')
        tracker.start()
        os.environ["CODECARBON_SERVER_LIFETIME"] = "1"

    try:
        print(f"Server is running at: http://127.0.0.1:{port}")
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Failed to start Website Server: {e}")
    finally:
        if tracker:
            try:
                emissions_kg = tracker.stop()
                if emissions_kg is None:
                    print("[CodeCarbon] Server lifetime emissions unavailable.")
                else:
                    print(f"[CodeCarbon] Server lifetime emissions: {emissions_kg * 1e6:.6f} mg CO2-eq")
            finally:
                os.environ.pop("CODECARBON_SERVER_LIFETIME", None)
