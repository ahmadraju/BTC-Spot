import re
import requests
from bs4 import BeautifulSoup

# List of your Blogspot page URLs
BLOG_URLS = [
    "https://raw.githubusercontent.com/oxyx4/seeker-btc-wallet-bruteforcer/refs/heads/main/adresses.txt"
    # Add more URLs here
]

BLOCKCHAIN_API_URL = "https://blockchain.info/balance?active="

def extract_bitcoin_addresses(html):
    """Extract Bitcoin addresses from the webpage content using regex."""
    btc_address_pattern = r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'
    return re.findall(btc_address_pattern, html)

def check_balances(addresses):
    """Check balances for the given Bitcoin addresses using the Blockchain.info API in batches."""
    results = {}
    batch_size = 200  # Number of addresses per batch
    total_addresses = len(addresses)

    for i in range(0, total_addresses, batch_size):
        batch = addresses[i:i + batch_size]
        batch_query = "|".join(batch)  # Combine addresses with '|'

        try:
            response = requests.get(BLOCKCHAIN_API_URL + batch_query, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for addr in batch:
                    balance = data.get(addr, {}).get("final_balance", 0) / 1e8  # Convert from satoshi to BTC
                    if balance > 0:
                        results[addr] = balance  # Only include addresses with a positive balance
            else:
                print(f"Failed to fetch data for batch {i // batch_size + 1}, status code: {response.status_code}")
            
            # Print progress
            print(f"Checked {min(i + batch_size, total_addresses)}/{total_addresses} addresses...")
        except Exception as e:
            print(f"Error checking balances for batch {i // batch_size + 1}: {e}")
    return results

def save_balances_to_file(balances):
    """Save addresses with positive balances to a file."""
    with open("balance.txt", "a") as file:
        for addr, bal in balances.items():
            file.write(f"Address: {addr}, Balance: {bal} BTC\n")

def main():
    for url in BLOG_URLS:
        try:
            print(f"Processing {url}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text()

            # Extract Bitcoin addresses
            btc_addresses = extract_bitcoin_addresses(page_text)
            print(f"Found {len(btc_addresses)} Bitcoin addresses on {url}.")

            # Check balances
            if btc_addresses:
                balances = check_balances(btc_addresses)
                if balances:
                    print(f"Addresses with balances on {url}:")
                    for addr, bal in balances.items():
                        print(f"Address: {addr}, Balance: {bal} BTC")
                    # Save to file
                    save_balances_to_file(balances)
                else:
                    print("No balances found on this page.")
        except Exception as e:
            print(f"Error processing {url}: {e}")

if __name__ == "__main__":
    main()

