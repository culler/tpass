"""
TPass
"""
__version__ = '1.0a2'

import os
import sys
import subprocess
import tomlkit
from chacha import get_passphrase, ChaChaContext
from .totp import TOTPGenerator

class TPass:
    def __init__(self):
        home = os.environ['HOME']
        self.context = ChaChaContext(get_passphrase())
        filename = os.path.join(home, '.accounts.cha')
        if not os.path.exists(filename):
            self.create_data_file()
        decrypted = self.context.decrypt_file_to_bytes(filename)
        self.data = tomlkit.loads(decrypted.decode('utf-8'))

    def create_data_file(self):
        print('create_data_file')

usage = """Usage: tpass [account]
If an account is provided then the userid is printed and the password is
copied to the clipboard.  If run with no arguments an interactive session
is started for creating or editing account information.
"""

#Commands are "update" ??? 

if sys.platform == 'darwin':
    def copy_as_clip(text):
        proc = subprocess.Popen(['/usr/bin/pbcopy'], stdin=subprocess.PIPE)
        proc.communicate(text.encode('utf-8'))
        
def main():
    nargs = len(sys.argv)
    if nargs > 2:
        print(usage)
        sys.exit(1)
    if nargs == 1:
        print('interact')
        sys.exit(0)
    if nargs == 2:
        tpass = TPass()
        if sys.argv[1] in tpass.data:
            account = tpass.data[sys.argv[1]]
            print('userid:', account['userid'])
            copy_as_clip(account['password'])
            print('The password has been copied to your clipboard.')
            if 'totp_key' in account:
                key = account['totp_key'].encode('utf-8')
                generator = TOTPGenerator(key)
                generator()
            sys.exit(0)

    
        
