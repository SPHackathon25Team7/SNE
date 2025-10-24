"""
Smart Notification Engine Runner
Run this file to start the Flask application
"""

from app import app

if __name__ == '__main__':
    print("Starting Smart Notification Engine...")
    print("Dashboard will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000)