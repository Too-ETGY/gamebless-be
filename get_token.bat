@echo off
echo Getting authentication token...

curl -X POST ^
  "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyDHrZhP4XINErE4CBjCGA25WXiojNt798s" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@test.com\",\"password\":\"Test1234!\",\"returnSecureToken\":true}"