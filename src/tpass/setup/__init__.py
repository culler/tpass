import os
import chacha

def main():
    tpass_file = os.path.join(os.environ['HOME'], '.accounts.cha')
    if not os.path.exists(tpass_file):
        print('Welcome to tpass!')
        print("""
The pass phrase that you are about to enter will be needed whenever
you use tpass.  It is used to encrypt the file containing the login
credentials for all of the accounts that you manage with tpass.

The phrase is allowed to contain spaces and punctuation, but no line
breaks.  It should be long enough to be hard to guess but it also
should be easy for you to remember and to type reliably.  It should
fit on one line in a typical terminal window, to avoid issues when
displaying the pass phrase.

When you type the phrase you will see what you are typing and you
will be able to edit the line until you hit the <Enter> key.  When
you do that it will be erased from your terminal window.

Please write your pass phrase down before typing it, and give the
piece of paper to the executor of your estate for safekeeping.  (Also
explain why they may need it, and how to use it.)
""")
        plaintext = b''
    else:
        print('Type yes to confirm that you want to change your '
             'pass phrase.')
        answer = input('>')
        if answer != 'yes':
            return
        current = chacha.get_passphrase('current pass phrase: ')
        context = chacha.ChaChaContext(current)
        try:
            plaintext = context.decrypt_file_to_bytes(tpass_file)
        except chacha.BadPassword:
            print('Invalid pass phrase')
            return
        print('Enter your new pass phrase below.')
    new = chacha.get_passphrase()
    new2 = chacha.get_passphrase('pass phrase again: ')
    if new != new2:
        print('Phrases are different. Aborting.')
        return
    context = chacha.ChaChaContext(new)
    context.encrypt_file_from_bytes(plaintext, tpass_file)
    
