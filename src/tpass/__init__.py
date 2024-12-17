"""
TPass
"""
__version__ = '1.0a5'

import os
import sys
import subprocess
import tomlkit
from chacha import get_passphrase, ChaChaContext
from .totp import TOTPGenerator

class TPass:
    def __init__(self):
        home = os.environ['HOME']
        self.filename = filename = os.path.join(home, '.accounts.cha')
        if not os.path.exists(filename):
            self.create_data_file()
        self.context = ChaChaContext(get_passphrase())
        decrypted = self.context.decrypt_file_to_bytes(filename)
        self.data = tomlkit.loads(decrypted.decode('utf-8'))

    def create_data_file(self):
        print('create a data file')

    def save(self):
        plaintext = tomlkit.dumps(self.data).encode('utf-8')
        self.context.encrypt_file_from_bytes(plaintext, self.filename)

    def add_account(self, account):
        print('add a new account', account)

    def interact(self):
        level, account, key, value, changed = 0, '', '', '', False
        while True:
            match level:
                case 0:  # set account
                    account = input('account > ')
                    if not account:
                        break
                    if not account in self.data:
                        self.add_account(account)
                    answer = input(
                        'Type view to view the account; '
                        'type delete to delete it;'
                        'hit <Enter> to continue: ')
                    # handle delete here.
                    if answer == 'view':
                        for key in self.data[account]:
                            if key == 'password':
                                print('password = <hidden>')
                            else:
                                value = self.data[account][key]
                                print('%s = "%s"' % (key, value))
                    level = 1
                case 1: # choose key
                    key = input('key >> ')
                    if not key:
                        level = 0
                    else:
                        level = 2
                case 2: # set value
                    value = input('value >>> ')
                    if value and value[0] == '"' and value[-1] == '"':
                        print('Quotation marks are not needed.')
                    value = value.strip('"')
                    if not value:
                        if not key in ('userid', 'password'):
                            answer = input('Type delete to delete the key %s; '
                            'hit <Enter> to continue: ' % key)
                            if answer == 'delete':
                                self.data[account].pop(key)
                                changed = True
                        level = 1
                    else:
                        print(key, '->', value)
                        self.data[account][key] = value
                        changed = True
                        level = 0
        if changed:
            print('changed')
            self.save()

usage = """Usage: tpass [account]
If an account is provided then the userid is printed and the password is
copied to the clipboard.  If run with no arguments an interactive session
is started for creating or editing account information.
"""

if sys.platform == 'darwin':
    clip_command = ['/usr/bin/pbcopy']
elif sys.platform in ('linux', 'linux2'):
    clip_command = ['/usr/bin/xsel', '-p']
else:
    clip_command = ['clip']
    
def copy_as_clip(text):
    proc = subprocess.Popen(clip_command, stdin=subprocess.PIPE)
    proc.communicate(text.encode('utf-8'))
        
def main():
    nargs = len(sys.argv)
    if nargs > 2 or nargs == 2 and sys.argv[1] in ('-h', '-help'):
        print(usage)
        sys.exit(1) 
    tpass = TPass()
    if nargs == 1:
        tpass.interact()
        sys.exit(0)
    if nargs == 2:
        account_name = sys.argv[1]
        if account_name in tpass.data:
            account = tpass.data[sys.argv[1]]
            print('userid:', account['userid'])
            copy_as_clip(account['password'])
            print('The password has been copied to your clipboard.')
            if 'totp_key' in account:
                key = account['totp_key'].encode('utf-8')
                generator = TOTPGenerator(key)
                generator()
        else:
            print("Unknown account:", account_name)
            answer = input(
                'Type yes to view known accounts, <Enter> to quit ')
            if answer == 'yes':
                for name in sorted(tpass.data.keys()):
                    print(name)
