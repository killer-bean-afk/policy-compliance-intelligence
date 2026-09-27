"""
Single-command runner script for Policy Compliance Intelligence Platform.
Launches Uvicorn server hosting backend REST APIs and frontend web dashboard.
"""

import sys
import os
import uvicorn

# Ensure backend directory is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

if __name__ == "__main__":
    print("========================================================================")
    print("  POLICY COMPLIANCE INTELLIGENCE PLATFORM")
    print("  Multi-Agent Evidence Grounded Assessment Microservice")
    print("========================================================================")
    print("  Backend API & Frontend Dashboard: http://localhost:8000")
    print("  Interactive API Documentation:  http://localhost:8000/docs")
    print("========================================================================\n")

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
