import subprocess


def main():
    subprocess.call(['coverage', 'run', '-m', 'pytest'])
    print('\n\nTests completed, checking coverage...\n\n')
    subprocess.call(['coverage', 'combine', '--append'])
    subprocess.call(['coverage', 'report', '-m'])
    input('\n\nPress enter to quit ')

if __name__ == '__main__':
    main()
