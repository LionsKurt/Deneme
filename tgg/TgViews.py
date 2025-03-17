import random
import sys
import os
import time
import threading
import concurrent.futures
from colorama import Fore, init
from time import sleep
from threading import Thread, active_count

# Initialize colorama
init(autoreset=True)

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    os.system('pip install requests')
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

# Colors
R = '\033[1;31;40m'
G = '\033[1;32;40m'
Y = '\033[1;33;40m' 
C = "\033[1;97;40m" 
B = '\033[1;36;40m'
P = '\033[1;35;40m'

# Statistics
successful_views = 0
failed_views = 0
total_proxies = 0
active_proxies = 0
last_view_count = "0"

def combo(s, speed=5):
    for char in s + '\n':
        sys.stdout.write(char)
        sys.stdout.flush()
        sleep(speed / 4000)

# Display program header
print(f"\n{B}{'='*50}")
combo(P + "       🚀 Telegram View Booster 🚀", 10)
combo(B + "         DrSudo Edition", 10)
print(f"{B}{'='*50}\n")

# Setup session with retries
def create_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry, pool_connections=100, pool_maxsize=100)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    })
    return session

# Ask for Telegram post URL
combo(P + "Enter a public Telegram channel post link:")
post_link = input(f'{Y}Post Link: {G}')

# Process post link
try:
    if "t.me" not in post_link:
        print(f"{R}Invalid URL! Make sure it's a t.me link.")
        sys.exit(1)
    
    if not post_link.startswith("https://"):
        post_link = "https://" + post_link
        
    parts = post_link.split('/')
    channel_name = parts[3]
    message_id = parts[4].split('?')[0]  # Remove any query parameters
    
    print(f"{G}Target: {B}https://t.me/{channel_name}/{message_id}")
except Exception as e:
    print(f"{R}Error parsing URL: {str(e)}")
    print(f"{Y}Expected format: https://t.me/channel_name/message_id")
    sys.exit(1)

# Display stats in a separate thread
def display_stats():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{B}{'='*50}")
        print(f"{P}🚀 Telegram View Booster - Running")
        print(f"{B}{'='*50}")
        print(f"{G}Target: {Y}https://t.me/{channel_name}/{message_id}")
        print(f"{G}Views Sent: {Y}{successful_views}")
        print(f"{R}Failed Attempts: {Y}{failed_views}")
        print(f"{B}Current View Count: {Y}{last_view_count}")
        print(f"{B}Active Proxies: {Y}{active_proxies}/{total_proxies}")
        print(f"{B}Active Threads: {Y}{active_count()}")
        print(f"{B}{'='*50}")
        print(f"{Y}Press Ctrl+C to stop the program")
        time.sleep(2)

# Function to send view
def send_view(proxy, timeout=10):
    global successful_views, failed_views, last_view_count, active_proxies
    
    proxy_type = 'http'
    if proxy.startswith('socks'):
        proxy_type = 'socks5'
    
    proxies = {
        'http': proxy,
        'https': proxy
    }
    
    try:
        session = create_session()
        
        # First request - get cookies
        response = session.get(
            f"https://t.me/{channel_name}/{message_id}", 
            timeout=timeout,
            proxies=proxies
        )
        
        if response.status_code != 200:
            failed_views += 1
            return False
        
        cookies = response.cookies
        if not cookies:
            cookie_header = response.headers.get('set-cookie')
            if cookie_header:
                # Parse cookies from header if no cookie jar
                cookie_parts = cookie_header.split(';')[0].split('=')
                if len(cookie_parts) >= 2:
                    name, value = cookie_parts[0], cookie_parts[1]
                    cookies.set(name, value)
        
        # Second request - get view key
        embed_url = f'https://t.me/{channel_name}/{message_id}?embed=1'
        response = session.get(
            embed_url,
            timeout=timeout,
            proxies=proxies
        )
        
        if 'data-view=' not in response.text:
            failed_views += 1
            return False
        
        # Extract view key and current count
        view_key = response.text.split('data-view="')[1].split('"')[0]
        
        try:
            view_count_part = response.text.split('<span class="tgme_widget_message_views">')[1].split('</span>')[0]
            last_view_count = view_count_part.strip()
        except:
            pass
        
        # Final request - send the view
        view_url = f'https://t.me/v/?views={view_key}'
        view_response = session.get(
            view_url,
            timeout=timeout,
            proxies=proxies,
            headers={"Referer": embed_url, "X-Requested-With": "XMLHttpRequest"}
        )
        
        if view_response.text == "true":
            successful_views += 1
            return True
        else:
            failed_views += 1
            return False
            
    except Exception as e:
        failed_views += 1
        return False

# Function to fetch proxies
def fetch_proxies():
    global total_proxies
    
    proxies = []
    proxy_apis = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt"
    ]
    
    print(f"{Y}Fetching proxies...")
    
    for api in proxy_apis:
        try:
            response = requests.get(api, timeout=20)
            if response.status_code == 200:
                new_proxies = response.text.strip().split('\n')
                for proxy in new_proxies:
                    proxy = proxy.strip()
                    if proxy and proxy not in proxies:
                        if "socks4" in api:
                            proxies.append(f"socks4://{proxy}")
                        elif "socks5" in api:
                            proxies.append(f"socks5://{proxy}")
                        else:
                            proxies.append(proxy)
                print(f"{G}Fetched {len(new_proxies)} proxies from {api.split('/')[2]}")
        except Exception as e:
            print(f"{R}Failed to fetch from {api}: {e}")
    
    # Remove duplicates and empty values
    proxies = list(set(filter(None, proxies)))
    total_proxies = len(proxies)
    
    print(f"{G}Total unique proxies: {total_proxies}")
    return proxies

# Worker function for thread pool
def worker(proxy):
    global active_proxies
    
    active_proxies += 1
    result = send_view(proxy)
    active_proxies -= 1
    
    return result

# Main function
def main():
    try:
        # Start stats display thread
        stats_thread = Thread(target=display_stats, daemon=True)
        stats_thread.start()
        
        while True:
            # Fetch fresh proxies
            proxies = fetch_proxies()
            
            if not proxies:
                print(f"{R}No proxies found. Retrying in 30 seconds...")
                time.sleep(30)
                continue
            
            print(f"{G}Starting view boost with {len(proxies)} proxies")
            
            # Use thread pool for better performance
            with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
                executor.map(worker, proxies)
            
            print(f"{Y}Completed cycle. Fetching new proxies...")
            time.sleep(5)  # Small delay between cycles
            
    except KeyboardInterrupt:
        print(f"\n{Y}Program stopped by user.")
    except Exception as e:
        print(f"\n{R}Error in main: {str(e)}")

if __name__ == "__main__":
    main()