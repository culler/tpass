"""
TPass
"""
__version__ = '1.0a5'

import os
import sys
import subprocess
import tomlkit
import readline
from chacha import get_passphrase, ChaChaContext
from .totp import TOTPGenerator

class TPass:
    def __init__(self):
        home = os.environ['HOME']
        self.filename = filename = os.path.join(home, '.accounts.cha')
        if not os.path.exists(filename):
            print('The encrypted credentials file does not exist.')
            print('Use the tpass-setup command to initialize it.')
        self.context = ChaChaContext(get_passphrase())
        decrypted = self.context.decrypt_file_to_bytes(filename)
        self.data = tomlkit.loads(decrypted.decode('utf-8'))

    def save(self):
        plaintext = tomlkit.dumps(self.data).encode('utf-8')
        self.context.encrypt_file_from_bytes(plaintext, self.filename)

    def add_account(self, account):
        new_account = tomlkit.table()
        print('Creating a new account named', account)
        print('The domain, username and password fields are required.')
        domain = input('domain: ')
        if not domain:
            print('Aborting.')
            return
        new_account.add('domain', domain)
        username = input('username: ')
        if not username:
            print('Aborting.')
            return
        new_account.add('username', username)
        password = input('password: ')
        if not password:
            print('Aborting.')
            return
        new_account.add('password', password)
        self.data[account] = new_account
        self.save()

    def interact(self):
        depth, account, key, value, changed = 0, '', '', '', False
        while True:
            match depth:
                case 0: # Choose Account
                    print('Type ? to view accounts, <Enter> to continue.')
                    match input('> '):
                        case '?':
                            for account in sorted(self.data.keys()):
                                print(account)
                        case '':
                            account = input('account: ')
                            if not account:
                                break
                            if account not in self.data:
                                self.add_account(account)
                            depth = 1
                        case _:
                            break
                case 1:  #  Delete the account or choose a key
                    print('Type ? to view %s, delete to delete it, '
                              '<Enter> to continue.' % account)
                    match input('> '):
                        case '?':
                            for key in self.data[account]:
                                if key == 'password':
                                    value = '<hidden>'
                                else:
                                    value = self.data[account][key]
                                print('  %s = "%s"' % (key, value))
                        case '':
                            key = input('key: ')
                            depth = 2 if key else 0
                            print('1: set depth to', depth)
                        case 'delete':
                            self.data.pop(account)
                            changed = True
                            depth = 0
                        case _:
                            depth = 0
                case 2: # Delete the key or set its value
                    if key not in ('userid', 'password'):
                        print('Type delete to delete %s, '
                              '<Enter> to set its value.' % key)
                        match input('> '):
                            case '':
                                value = input('value: ')
                            case 'delete':
                                self.data[account].pop(key)
                                changed = True
                                value = ''
                                depth = 1
                            case _:
                                value = ''
                                depth = 0                                
                    else:
                        value = input('value: ')
                    if value:
                        stripped = value.strip('"')
                        if len(stripped) < len(value):
                            print('Quotation marks are not needed, '
                                  'and will be removed.')
                        value = stripped
                        self.data[account][key] = value
                        changed = True
                        key = input('key: ')
                        if not key:
                            depth = 0
                        print('2: set depth to', depth)
                    else:
                        depth = 0
        if changed:
            self.save()

usage = """Usage: tpass <account>
The userid for the specified account is printed and the password is
copied to the clipboard.

To initialize an encrypted credentials file, or to change the pass
phrase on an existing credentials file, use the tpass-setup command.

To edit data in the encrypted credentials file, use the tpass-edit
command.
"""

if sys.platform == 'darwin':
    clip_commands = [['/usr/bin/pbcopy']]
elif sys.platform in ('linux', 'linux2'):
    if "WAYLAND_DISPLAY" in os.environ:
        clip_commands = [['/usr/bin/wl-copy', '-p'], ['/usr/bin/wl-copy']]
    elif "DISPLAY" in os.environ:
        clip_commands = [['/usr/bin/xsel', '-p', '-c']]
    else:
        print("An X11 or Wayland server is required to use the clipboard.")
else:
    clip_command = ['clip']
    
def copy_as_clip(text):
    for command in clip_commands:
        proc = subprocess.Popen(command, stdin=subprocess.PIPE)
        proc.communicate(text.encode('utf-8'))
        
def main():
    nargs = len(sys.argv)
    if nargs != 2 or nargs == 2 and sys.argv[1] in ('-h', '-help'):
        print(usage)
        sys.exit(1) 
    tpass = TPass()
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
