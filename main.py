import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from simpleBrowsergui import Ui_MainWindow  # GUI layout from simpleBrowsergui.py
from browserFunctions import BrowserFunctions  # Browser functionality from browserFunctions.py
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut
from PyQt5.QtGui import QKeySequence
import html

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Setup the UI from the simpleBrowsergui.py
        self.browser_functions = BrowserFunctions(self)  # Initialize browser functions

        # Create a shortcut for F12 to toggle developer tools
        self.shortcutF12 = QShortcut(QKeySequence('F12'), self)
        self.shortcutF12.activated.connect(self.toggle_dev_tools)

        # Initially hide the developer tools components
        self.domTree.hide()
        self.htmlEditor.hide()
        self.devToolsDockWidget.hide()
        self.webEngineView.page().loadFinished.connect(self.load_page_html_to_html_editor)

        # A flag to check if the page has changed
        self.page_changed = False
        # Save the original key press event of the HTML editor
        self.original_keyPressEvent = self.htmlEditor.keyPressEvent
        # Override the key press event to handle Enter key
        self.htmlEditor.keyPressEvent = self.on_key_press_in_html_editor

        # Set the initial URL of the web view to Google
        self.webEngineView.setUrl(QtCore.QUrl("https://www.google.com"))
        
    def toggle_dev_tools(self):
        # Toggle visibility of developer tools components
        if self.domTree.isVisible():
            self.domTree.hide()
            self.htmlEditor.hide()
            self.devToolsDockWidget.hide()
        else:
            self.domTree.show()
            self.htmlEditor.show()
            self.devToolsDockWidget.show()
            # Connect load finished signal to slot if the page has changed
            if not self.page_changed:
                self.webEngineView.page().loadFinished.connect(self.load_page_html_to_html_editor)
                self.page_changed = True

    def load_page_html_to_html_editor(self):
        # Load the HTML of the current page into the HTML editor
        self.webEngineView.page().toHtml(self.fill_html_editor)

    def fill_html_editor(self, html_content):
        # Fill the HTML editor with the page's HTML
        self.htmlEditor.clear()
        self.htmlEditor.setPlainText(html_content)

    def on_key_press_in_html_editor(self, event):
        # Override the key press event in the HTML editor
        if event.key() == QtCore.Qt.Key_Return:
            # Apply changes when Enter is pressed
            modified_html = self.htmlEditor.toPlainText()
            self.apply_html_changes(modified_html)
        else:
            event.ignore()

    def apply_html_changes(self, html_content):
        # Apply changes made in the HTML editor to the web view
        escaped_html = html_content.replace("'", "\\'").replace('\n', '')
        js_code = f"document.body.innerHTML = '{escaped_html}';"
        self.webEngineView.page().runJavaScript(js_code)

# The main execution starts here
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()  # Show the main window
    sys.exit(app.exec_())  # Start the application's event loop
