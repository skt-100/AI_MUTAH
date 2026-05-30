import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Src'))
from API.server import create_server
from API import settings as st
server = create_server()
if __name__ == '__main__':
    server.run(host=st.FLASK_HOST, port=st.FLASK_PORT, debug=st.FLASK_DEBUG)
