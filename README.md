1. To run in localhost:
   ```uvicorn main:app --reload```
2. To check .env (postgres data) in linux:
   ```nano chatbot_cirebon/.env```
3. To stop background chatbot program run in linux:
   ```systemctl status uv.cirebon.service```
4. To restart background chatbot program in linux:
   ```systemctl start uv.cirebon.service```
5. To check error log in linux:
   ```tail -f /var/log/uv.cirebon.log```
6. To check background run status:
   ```systemctl status uv.cirebon.service```
   
