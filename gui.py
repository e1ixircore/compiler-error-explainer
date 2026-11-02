import logging
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
    try:
        app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Failed to start Website Server: {e}")
