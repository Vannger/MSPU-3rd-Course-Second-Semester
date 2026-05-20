import os
import sys
from dotenv import load_dotenv

load_dotenv()

secret = os.getenv("APP_SECRET")

if not secret:
  print("Error: there's no password! Check the file")
  sys.exit(1)

masked_secret = secret[:3] + "***"
print(f"System started. Secret hash: {masked_secret}")
