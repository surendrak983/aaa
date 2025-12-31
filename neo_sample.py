import os
import neo_api_client
from neo_api_client import NeoAPI
import logging

# --- Configure Logging ---
# It's a good practice to set up logging to see the library's output.
logging.basicConfig(level=logging.DEBUG)

# --- User Credentials (TO BE FILLED BY THE USER) ---
# It's recommended to use environment variables for security.
# You can set them in your terminal like this:
# export NEO_CONSUMER_KEY="your_consumer_key"
# export NEO_MOBILE_NUMBER="your_mobile_number"
# export NEO_UCC="your_ucc"
# export NEO_MPIN="your_mpin"
# export NEO_TOTP="your_totp"

consumer_key = os.getenv("NEO_CONSUMER_KEY", "YOUR_TOKEN")
mobile_number = os.getenv("NEO_MOBILE_NUMBER", "")
ucc = os.getenv("NEO_UCC", "")
mpin = os.getenv("NEO_MPIN", "")
totp = os.getenv("NEO_TOTP", "") # Time-based OTP from your authenticator app

# --- WebSocket Event Handlers ---
def on_message(message):
    """Callback function to handle incoming WebSocket messages."""
    print(f"Received WebSocket message:\n{message}")

def on_error(error_message):
    """Callback function to handle WebSocket errors."""
    print(f"WebSocket Error: {error_message}")

def on_close(message):
    """Callback function for when the WebSocket connection is closed."""
    print(f"WebSocket connection closed: {message}")

def on_open(message):
    """Callback function for when the WebSocket connection is opened."""
    print(f"WebSocket connection opened: {message}")


def main():
    """
    Main function to demonstrate the usage of the Kotak Neo API client.
    """
    print("--- Initializing Kotak Neo API Client ---")
    # Initialize the NeoAPI client
    # 'prod' is for the live environment.
    client = NeoAPI(
        environment='prod',
        consumer_key=consumer_key,
        access_token=None,  # Will be obtained after login
        neo_fin_key=None    # Optional, pass None
    )

    # --- Step 1: Login using TOTP ---
    print("\n--- Performing TOTP Login ---")
    if not all([mobile_number, ucc, totp]):
        print("Please set NEO_MOBILE_NUMBER, NEO_UCC, and NEO_TOTP environment variables.")
        return

    try:
        login_response = client.totp_login(
            mobile_number=mobile_number,
            ucc=ucc,
            totp=totp
        )
        print("TOTP Login successful!")
        print(f"Login Response: {login_response}")
    except Exception as e:
        print(f"TOTP Login failed: {e}")
        return

    # --- Step 2: Validate with MPIN ---
    print("\n--- Performing TOTP Validation with MPIN ---")
    if not mpin:
        print("Please set NEO_MPIN environment variable.")
        return

    try:
        validate_response = client.totp_validate(mpin=mpin)
        print("TOTP Validation successful!")
        print(f"Validation generates the trade token: {validate_response}")
    except Exception as e:
        print(f"TOTP Validation failed: {e}")
        return


    # --- Step 3: Fetching Data (Example: Order Report) ---
    # You need to be logged in to access most of these endpoints.
    print("\n--- Fetching Order Report ---")
    try:
        order_report = client.order_report()
        print("Successfully fetched order report:")
        print(order_report)
    except Exception as e:
        print(f"Failed to fetch order report: {e}")


    # --- Step 4: Using WebSockets for Live Data ---
    print("\n--- Subscribing to Live Market Data ---")
    # Set up the WebSocket event handlers
    client.on_message = on_message
    client.on_error = on_error
    client.on_close = on_close
    client.on_open = on_open

    # Example: Subscribe to get data for a specific stock
    # You need to get the instrument_token from the scrip_master file.
    # For this example, let's assume a token.
    instrument_tokens = [
        {"instrument_token": "26000", "exchange_segment": "nse_cm"}, # Example: NIFTY 50 Index
    ]

    try:
        # Subscribe to the instrument
        # isIndex=True is needed for index instruments
        client.subscribe(instrument_tokens=instrument_tokens, isIndex=True, isDepth=False)
        print(f"Subscribed to instruments: {instrument_tokens}")
        print("Waiting for WebSocket messages... (Press Ctrl+C to exit)")

        # Keep the script running to receive messages
        import time
        time.sleep(30) # Wait for 30 seconds to receive some data

        # Unsubscribe from the instruments
        print("\n--- Unsubscribing from Live Market Data ---")
        client.un_subscribe(instrument_tokens=instrument_tokens, isIndex=True)
        print("Unsubscribed successfully.")

    except Exception as e:
        print(f"WebSocket subscription failed: {e}")


    # --- Step 5: Logout ---
    print("\n--- Logging out ---")
    try:
        logout_response = client.logout()
        print(f"Logout successful: {logout_response}")
    except Exception as e:
        print(f"Logout failed: {e}")

if __name__ == "__main__":
    main()
