import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Bot setup with proper intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message_content intent
bot = commands.Bot(command_prefix='!', intents=intents)

# Global WebDriver to reuse the session
driver = None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def search(ctx, sim_number: str):
    global driver
    try:
        # Notify that the search is starting
        await ctx.send("🔍 Searching in KING's Database...")

        # Set up the driver if not already done
        driver = setup_driver()

        # Open the page
        driver.get("https://simdata.store/")
        print("Page loaded successfully")

        # Wait for the search box to be present
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'query')))
        print("Search box found")

        # Input the search number and submit
        search_box = driver.find_element(By.NAME, 'query')
        search_box.send_keys(sim_number)
        search_box.submit()
        print("Search submitted")

        # Wait for results to load
        time.sleep(5)  # Adjust if necessary, depending on the website's response time

        # Optionally check the page source for debug info
        page_source = driver.page_source
        print("Page source fetched")

        # Extract the results
        result_elements = driver.find_elements(By.CSS_SELECTOR, 'tbody tr td')
        if len(result_elements) >= 5:
            results = {
                "Name": result_elements[0].text,
                "Mobile": result_elements[1].text,
                "CNIC": result_elements[2].text,
                "Operator": result_elements[3].text,
                "Address": result_elements[4].text
            }

            # Create an embed for the result
            embed = discord.Embed(title=f"Results for SIM Number {sim_number}", color=0x00ff00)
            embed.add_field(name="👤 Name", value=results['Name'], inline=False)
            embed.add_field(name="📱 Mobile", value=results['Mobile'], inline=False)
            embed.add_field(name="🆔 CNIC", value=results['CNIC'], inline=False)
            embed.add_field(name="📶 Operator", value=results['Operator'], inline=False)
            embed.add_field(name="🏠 Address", value=results['Address'], inline=False)

            await ctx.send(embed=embed)
            print(f"Results found and sent for {sim_number}")  # Debug: Print success message
        else:
            await ctx.send("Sorry This Number is Not Available in King Database. After the update, this number's details may get added.")
            print(f"No results found for {sim_number}")  # Debug: Print no results message

    except Exception as e:
        await ctx.send("❗ An error occurred while searching. Please try again later.")
        print(f"Error during search: {e}")  # Debug: Print the error

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')

    # Check if the driver is already running, if so, reuse it
    global driver
    if not driver:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    return driver

# Ensure to stop the driver when the bot shuts down
@bot.event
async def on_disconnect():
    if driver:
        driver.quit()

# Your provided bot token
bot.run('MTI3ODI3NjEwMDY4MTYyOTcwNg.GWB6ek.X5NRZjoKyVZ1r1ZGRY37puJ3KNA7bGVJhI_s70')
