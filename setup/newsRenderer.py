from PySide6.QtCore import QThread, Qt, QObject, Signal
from PySide6.QtWidgets import QLabel, QSizePolicy
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

class NewsWorker(QObject):
    """Worker to fetch news in a separate thread"""
    news_fetched = Signal(list)  # Changed to accept a list of news items
    error = Signal(str)
    finished = Signal()
    
    def fetch_news(self):
        try:
            # Fetch the RSS feed
            response = requests.get("https://wiilink.ca/rss.xml", timeout=5)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.text)
            
            # Get up to 3 latest news items
            items = root.findall('.//item')[:3]  # Get first 3 items
            
            if items:
                news_items = []
                for item in items:
                    title = item.find('title').text
                    link = item.find('link').text
                    
                    # Parse and format the date
                    pub_date = item.find('pubDate').text
                    try:
                        date_obj = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
                        formatted_date = date_obj.strftime("%B %d, %Y")
                    except:
                        formatted_date = pub_date
                    
                    author = item.find('author').text if item.find('author') is not None else "WiiLink Team"
                    
                    news_items.append({
                        'title': title,
                        'link': link,
                        'date': formatted_date,
                        'author': author
                    })
                
                self.news_fetched.emit(news_items)
            else:
                self.error.emit("No news items found")
        except requests.RequestException as e:
            self.error.emit(f"Network error: {str(e)}")
        except ET.ParseError as e:
            self.error.emit(f"Invalid RSS format: {str(e)}")
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

class NewsRenderer:
    """A class to handle news rendering in a modular way"""
    
    @staticmethod
    def createNewsBox(parent):
        """Creates and returns a styled news box label"""
        news_box = QLabel(parent)
        news_box.setWordWrap(True)
        news_box.setStyleSheet("""
            background-color: #333333;
            color: white;
            border: 1px solid #555555;
            border-radius: 5px;
            padding: 10px;
            font-size: 12px;
        """)
        news_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        news_box.adjustSize()
        news_box.setText("Loading latest news...")
        news_box.setAlignment(Qt.AlignmentFlag.AlignLeft)
        news_box.setTextFormat(Qt.TextFormat.RichText)
        news_box.setOpenExternalLinks(True)
        
        return news_box
    
    @staticmethod
    def getNews(parent, news_box):
        """Starts the news fetching process
        
        Args:
            parent: The parent widget (used for thread connections)
            news_box: The QLabel to update with news
            
        Returns:
            None
        """
        try:
            # Create thread for news fetching
            news_thread = QThread(parent)
            news_worker = NewsWorker()
            
            # Move worker to thread
            news_worker.moveToThread(news_thread)
            news_thread.started.connect(news_worker.fetch_news)
            
            # Connect signals
            news_worker.news_fetched.connect(lambda items: NewsRenderer._update_news(news_box, items))
            news_worker.error.connect(lambda error: NewsRenderer._handle_error(news_box, error))
            
            # Cleanup connections
            news_worker.finished.connect(news_thread.quit)
            news_thread.finished.connect(news_worker.deleteLater)
            news_thread.finished.connect(news_thread.deleteLater)
            
            # Store thread and worker references in parent to prevent garbage collection
            parent.news_thread = news_thread
            parent.news_worker = news_worker
            
            # Start the thread
            news_thread.start()
            
        except Exception as e:
            news_box.setText(f"<b>WiiLink News</b><br>Could not load news: {str(e)}")
    
    @staticmethod
    def _update_news(news_box, news_items):
        """Updates the news box with fetched news items"""
        news_html = "<span style='font-size: 16px;'><b>Latest WiiLink News</b></span><br><br>"
        
        # Process each news item
        for i, item in enumerate(news_items):
            # Add the news item title and metadata
            news_html += f"""<b><a href="{item['link']}" style="color: #3498db; text-decoration: none;">{item['title']}</a></b><br>
                         <i>{item['date']} - {item['author']}</i>"""
            
            # Only add extra line breaks if it's not the last item
            if i < len(news_items) - 1:
                news_html += "<br><br>"
        
        news_box.setText(news_html)
    
    @staticmethod
    def _handle_error(news_box, error):
        """Handles errors when fetching news"""
        news_box.setText(f"<b>WiiLink News</b><br>Could not load news: {error}")