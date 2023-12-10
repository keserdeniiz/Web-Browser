import re
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5 import QtCore

class BrowserFunctions:
    def __init__(self, ui):
        # Initialize the browser functions and UI elements
        self.ui = ui
        self.history = []  # Stores the browsing history
        self.current_index = -1  # Tracks the current page index in history

        # Connecting UI buttons to their respective functions
        self.ui.backButton.clicked.connect(self.backPage)
        self.ui.forwardButton.clicked.connect(self.forwardPage)
        self.ui.refreshButton.clicked.connect(self.refreshPage)
        self.ui.goButton.clicked.connect(self.goPage)

        # Connecting web engine signals to slot methods
        self.ui.webEngineView.loadFinished.connect(self.onLoadFinished)
        self.ui.webEngineView.urlChanged.connect(self.onUrlChanged)
        self.ui.lineEdit.returnPressed.connect(self.goPage)

        #History
        self.ui.historyButton.clicked.connect(self.displayHistory)

    def displayHistory(self):
        # Create a message with browsing history
        history_message = "\n".join(self.history)
        QMessageBox.information(self.ui, "Browsing History", history_message)


    def backPage(self):
        # Go to the previous page in history
        if self.current_index > 0:
            self.current_index -= 1
            self.loadPage(self.history[self.current_index])

    def forwardPage(self):
        # Go to the next page in history
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            self.loadPage(self.history[self.current_index])

    def refreshPage(self):
        # Refresh the current page
        if self.current_index >= 0:
            self.loadPage(self.history[self.current_index])

    def goPage(self):
        # Load the page from the address in the line edit
        url = self.ui.lineEdit.text().strip()
        if not url.startswith(('http://', 'https://')):
            # If the URL doesn't start with http:// or https://, assume it's a Google search
            url = 'https://www.google.com/search?q=' + url.replace(' ', '+')
        elif url.startswith('http://'):
            # Convert http to https for security
            url = 'https://' + url[7:]
        self.loadPage(url)

    def loadPage(self, url):
        # Load the specified URL in the web view
        self.ui.webEngineView.setUrl(QUrl(url))
        self.ui.lineEdit.setText(url)
        # Update history if the URL is new
        if self.current_index == -1 or self.history[self.current_index] != url:
            self.history = self.history[:self.current_index + 1]
            self.history.append(url)
            self.current_index = len(self.history) - 1

    def makeGetRequest(self, url):
        # Create and send a GET request
        manager = QNetworkAccessManager()
        request = QNetworkRequest(QUrl(url))
        reply = manager.get(request)
        reply.finished.connect(lambda: self.handleResponse(reply))

    def makePostRequest(self, url, data):
        # Create and send a POST request
        manager = QNetworkAccessManager()
        request = QNetworkRequest(QUrl(url))
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/x-www-form-urlencoded")
        reply = manager.post(request, data.encode())
        reply.finished.connect(lambda: self.handleResponse(reply))

    def handleResponse(self, reply):
        # Handle the response from a network request
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll()
            QMessageBox.information(self.ui, "Response", f"Received data: {data}")
        else:
            QMessageBox.warning(self.ui, "Error", f"Error: {reply.errorString()}")

    def onUrlChanged(self, url):
        # Update the address bar when the URL changes
        current_url = url.toString()
        self.ui.lineEdit.setText(current_url)
        # Update history if the URL is new
        if self.current_index == -1 or self.history[self.current_index] != current_url:
            self.history = self.history[:self.current_index + 1]
            self.history.append(current_url)
            self.current_index += 1

    def onLoadFinished(self, success):
        # Update the address bar when a page load finishes
        if success:
            current_url = self.ui.webEngineView.url()
            self.ui.lineEdit.setText(current_url.toString())
