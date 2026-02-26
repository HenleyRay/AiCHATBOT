# Troubleshooting - Server Can't Be Reached

## Server Status: ✅ RUNNING
The server is listening on port 5000 (process ID 3512).

## Try These Solutions:

### 1. Use 127.0.0.1 instead of localhost
Sometimes `localhost` doesn't resolve properly. Try:
```
http://127.0.0.1:5000
```

### 2. Check Your Browser
- Make sure you're using `http://` not `https://`
- Try a different browser (Chrome, Firefox, Edge)
- Clear your browser cache
- Try incognito/private mode

### 3. Check Windows Firewall
The server might be blocked by Windows Firewall:
1. Open Windows Defender Firewall
2. Click "Allow an app or feature through Windows Firewall"
3. Find Python and make sure it's allowed for Private networks
4. Or temporarily disable firewall to test

### 4. Check if Another App is Using Port 5000
Run this command:
```powershell
netstat -ano | findstr :5000
```
If you see multiple entries, there might be a conflict.

### 5. Restart the Server
Stop the current server (Ctrl+C in the terminal) and restart:
```powershell
python app.py
```

### 6. Try a Different Port
Edit `.env` file and change:
```
APP_PORT=5001
```
Then restart the server and try: `http://localhost:5001`

### 7. Check Server Logs
Look at the terminal where you ran `python app.py` - are there any error messages?

### 8. Test with PowerShell
Run this command to test the connection:
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:5000" -UseBasicParsing
```

## Current Server Status
- ✅ Port 5000 is LISTENING
- ✅ Process is running (PID: 3512)
- ⚠️  If you still can't connect, it might be a firewall or browser issue

## Quick Test
Open PowerShell and run:
```powershell
Start-Process "http://127.0.0.1:5000"
```

This should open your default browser to the chatbot.

