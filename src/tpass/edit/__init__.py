import sys
from tpass import TPass

def main():
    tpass = TPass()
    depth, account, key, value, changed = 0, '', '', '', False
    while True:
        match depth:
            case 0: # Choose Account
                print('Type ? to view accounts, <Enter> to continue, '
                      'Q to quit.')
                match input('> '):
                    case '?':
                        for account in sorted(tpass.data.keys()):
                            print(account)
                    case '':
                        account = input('account: ')
                        if not account:
                            break
                        if account not in tpass.data:
                            tpass.add_account(account)
                        depth = 1
                    case 'Q':
                        break
                    case _:
                        break
            case 1:  #  Delete the account or choose a key
                print(f'Type ? to view {account}, <Space> to delete it, '
                          '<Enter> to continue, ^ to go back.')
                match input('> '):
                    case '?':
                        for key in tpass.data[account]:
                            if key == 'password':
                                value = '<hidden>'
                            else:
                                value = tpass.data[account][key]
                            print(f'  {key} = "{value}"')
                    case '':
                        key = input('key: ')
                        depth = 2 if key else 0
                    case '^':
                        account = ''
                        depth = 0
                    case ' ':
                        msg = f'Type yes to confirm deletion of {account}: '
                        if input(msg) == 'yes':
                            tpass.data.pop(account)
                            changed = True
                    case _:
                        depth = 0
            case 2: # Delete the key or set its value
                if key not in ('userid', 'password'):
                    if key in tpass.data[account]:
                        print(f'Type <Space> to delete {key}, '
                              '<Enter> to set its value, ^ to go back.')
                        match input('> '):
                            case '':
                                value = input('value: ')
                            case '^':
                                key = ''
                                depth = 1
                            case ' ':
                                msg = f'Type yes to confirm deletion of {key}: '
                                if input(msg) == 'yes':
                                    tpass.data[account].pop(key)
                                    changed = True
                                    value = ''
                            case _:
                                value = ''
                                depth = 0                                
                    else:
                        value = input('value: ')
                else:
                    value = input('value: ')
                if value:
                    stripped = value.strip('"')
                    if len(stripped) < len(value):
                        print('Quotation marks are not needed, '
                              'and will be removed.')
                    value = stripped
                    tpass.data[account][key] = value
                    changed = True
                    key = input('key: ')
                    if not key:
                        depth = 1
                else:
                    depth = 1
    if changed:
        tpass.save()
