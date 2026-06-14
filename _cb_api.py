"""Check CloakBrowser API"""
from cloakbrowser import launch
browser = launch(headless=False)
print(type(browser))
print(dir(browser))
