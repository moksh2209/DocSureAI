import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to frontend...")
        await page.goto("http://localhost:5173")
        
        print("Uploading file...")
        await page.set_input_files('input[type="file"]', r'F:\project\DocSureAI\data\input\test_employee_record_4x3.png')
        
        print("Clicking process...")
        await page.click('button:has-text("Process Document")')
        
        print("Waiting for response...")
        try:
            await page.wait_for_selector('.results-container, .error-message', timeout=15000)
            
            error = await page.query_selector('.error-message')
            if error:
                text = await error.inner_text()
                print("UI ERROR FOUND:", text)
            else:
                print("Results rendered successfully!")
                
        except Exception as e:
            print("Timeout or error:", e)
            
        await page.screenshot(path="final_ui.png")
        await browser.close()

asyncio.run(run())
