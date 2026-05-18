#!/bin/bash
python3 -m uvicorn app.api:app --port 8001 > uvicorn.log 2>&1 &
API_PID=$!
sleep 3
# Update API_URL in the test file temporarily to 8001 to avoid conflicts
sed -i 's/8000/8001/' tests/safety_rig/router_leak_test.py
pytest tests/safety_rig/router_leak_test.py -v > rig_output.txt 2>&1
kill $API_PID
sed -i 's/8001/8000/' tests/safety_rig/router_leak_test.py
