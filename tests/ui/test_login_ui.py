import pytest
from playwright.sync_api import Page, expect

@pytest.mark.ui
def test_login_success(page: Page):
    page.goto("https://www.saucedemo.com/")        # sample demo site
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")

    # simple assertion
    expect(page.locator(".title")).to_have_text("Products")