import os
import sys

sys.path.append(os.getcwd())
os.environ["WIO_API_SSL_VERIFY"] = "0"
os.environ["WIO_API_URL"] = "https://localhost:1443/"
