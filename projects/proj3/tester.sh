# author: Archisa Bhattacharya

# Set your server IP and port
SERVER_IP="127.0.0.1"
SERVER_PORT="8080"

# Variables for storing session cookies
SESSION_COOKIE=""

# Common curl options for HTTP/1.0 and connection close
CURL_OPTIONS="--http1.0 --connect-timeout 5 --max-time 10 --fail --silent"

# 1. No Username (POST at the root)
printf "\nTest Case 1: No Username (POST at the root)\n"
SESSION_COOKIE=$(curl -i -v -X POST -H "password: 3TQI8TB39DFIMI6" "http://${SERVER_IP}:${SERVER_PORT}/" | grep -i 'Set-Cookie' | cut -d ' ' -f 2 | cut -d '=' -f 2)

# 2. No Password (POST at the root)
printf "\nTest Case 2: No Password (POST at the root)\n"
SESSION_COOKIE=$(curl -i -v -X POST -H "username: Richard" "http://${SERVER_IP}:${SERVER_PORT}/" | grep -i 'Set-Cookie' | cut -d ' ' -f 2 | cut -d '=' -f 2)

# 3. Username incorrect (POST at the root)
printf "\nTest Case 3: Username incorrect (POST at the root)\n"
SESSION_COOKIE=$(curl -i -v -X POST -H "username: Angela" -H "password: 3TQI8TB39DFIMI6" "http://${SERVER_IP}:${SERVER_PORT}/" | grep -i 'Set-Cookie' | cut -d ' ' -f 2 | cut -d '=' -f 2)

# 4. Password incorrect (POST at the root)
printf "\nTest Case 4: Password incorrect (POST at the root)\n"
SESSION_COOKIE=$(curl -i -v -X POST -H "username: Richard" -H "password: XMLU8ZPD7Z9BMC5" "http://${SERVER_IP}:${SERVER_PORT}/" | grep -i 'Set-Cookie' | cut -d ' ' -f 2 | cut -d '=' -f 2)

# 5. Username (1st username) correct/password correct (POST at the root)  SUCCESSFUL
printf "\nTest Case 5: Username (1st username) correct/password correct (POST at the root) CORRECT\n"  
SESSION_COOKIE=$(curl -i -v -X POST -H "username: Richard" -H "password: 3TQI8TB39DFIMI6" "http://${SERVER_IP}:${SERVER_PORT}/" | grep -i 'Set-Cookie' | cut -d ' ' -f 2 | cut -d '=' -f 2)

# 6. Username (1st username) correct/password correct (POST at the root) -> Generate a new cookie SUCCESSFUL
printf "\nTest Case 6: Username (1st username) correct/password correct (POST at the root) -> Generate a new cookie    CORRECT \n"
SESSION_COOKIE=$(curl -i -v -X POST -H "username: Richard" -H "password: 3TQI8TB39DFIMI6" "http://${SERVER_IP}:${SERVER_PORT}/" | grep -i 'Set-Cookie' | cut -d ' ' -f 2 | cut -d '=' -f 2)

# 7. Invalid cookie (GET)  
printf "\n# Test Case 7: Invalid cookie (GET)\n"
curl $CURL_OPTIONS -v -X GET -H "Cookie: sessionID=apple" "http://${SERVER_IP}:${SERVER_PORT}/file.txt"

# 8. Username (1st username) (GET filename for user 1) correct   SUCCESSFUL
printf "\n Test Case 8: Username (1st username) (GET filename for user 1) SUCCESSFUL\n"
curl $CURL_OPTIONS -v -X GET -H "Cookie: sessionID=$SESSION_COOKIE" "http://${SERVER_IP}:${SERVER_PORT}/file.txt"

# 9. Username (2nd username) correct/password correct (POST)   SUCCESSFUL
printf "\n# Test Case 9: Username (2nd username) correct/password (POST) SUCCESSFUL\n"
SESSION_COOKIE=$(curl -i -v -X POST -H "username: Angela" -H "password: XMLU8ZPD7Z9BMC5" "http://${SERVER_IP}:${SERVER_PORT}/" | grep -i 'Set-Cookie' | cut -d ' ' -f 2 | cut -d '=' -f 2)

# 10. GET file successful (GET filename for user 2)
printf "\nTest Case 10: GET file successful (GET filename for user 2)\n"
curl $CURL_OPTIONS -v -X GET -H "Cookie: sessionID=$SESSION_COOKIE" "http://${SERVER_IP}:${SERVER_PORT}/file.txt"

# 11. GET file not found (GET FAIL)
printf "\n# Test Case 11: GET file not found (GET FAIL)\n"
curl $CURL_OPTIONS -v -X GET -H "Cookie: sessionID=$SESSION_COOKIE" "http://${SERVER_IP}:${SERVER_PORT}/file2.txt"

# Sleep for 6 seconds
printf "\nSleeping for 6 seconds...\n"
sleep 6s

# 12. Expired cookie with username 2 (GET filename for user 2)
printf "\nTest Case 12: Expired cookie with username 2 (GET filename for user 2)\n"
curl $CURL_OPTIONS -v -X GET -H "Cookie: sessionID=$SESSION_COOKIE" "http://${SERVER_IP}:${SERVER_PORT}/file.txt"



