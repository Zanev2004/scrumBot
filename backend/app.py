from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import io
from csv_processor import process_csv_data

# Create Flask app
app = Flask(__name__)

# Enable CORS (allows frontend on different port to call this API)
CORS(app)

# Health check endpoint - test if server is running
@app.route('/health', methods=['GET'])
def health_check():
    """Simple endpoint to check if API is alive"""
    return jsonify({
        "status": "healthy",
        "message": "Scrumbot API is running"
    })

# Main CSV processing endpoint
@app.route('/api/process-csv', methods=['POST'])
def process_csv():
    """
    Process uploaded CSV file and return risk assessment.
    
    Expected: CSV file in request
    Returns: JSON with normalized data and risk scores
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                "error": "No file uploaded",
                "message": "Please upload a CSV file"
            }), 400  # 400 = Bad Request
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({
                "error": "Empty filename",
                "message": "Please select a file"
            }), 400
        
        # Check if it's a CSV file
        if not file.filename.endswith('.csv'):
            return jsonify({
                "error": "Invalid file type",
                "message": "Please upload a CSV file"
            }), 400
        
        # Read CSV data
        csv_data = file.read().decode('utf-8')
        
        # Process the CSV
        results = process_csv_data(csv_data)
        
        # Calculate summary statistics
        summary = {
            "total": len(results),
            "critical": sum(1 for r in results if r.get('risk_level') == 'CRITICAL'),
            "high": sum(1 for r in results if r.get('risk_level') == 'HIGH'),
            "medium": sum(1 for r in results if r.get('risk_level') == 'MEDIUM'),
            "low": sum(1 for r in results if r.get('risk_level') == 'LOW'),
            "unknown": sum(1 for r in results if r.get('risk_level') == 'UNKNOWN')
        }
        
        # Return success response
        return jsonify({
            "success": True,
            "results": results,
            "summary": summary
        }), 200  # 200 = Success
    
    except Exception as e:
        # If anything goes wrong, return error
        return jsonify({
            "error": "Processing failed",
            "message": str(e)
        }), 500  # 500 = Internal Server Error

# Run the server
if __name__ == '__main__':
    print("Starting Scrumbot API...")
    print("Health check: http://localhost:5000/health")
    print("API endpoint: http://localhost:5000/api/process-csv")
    app.run(debug=True, port=5000)