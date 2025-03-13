## **Project detail**
This project consists of two tasks aimed at developing tools for document retrieval and classification:

### Task 1: Search Engine
The goal is to design and implement a vertical search engine tailored to retrieve academic papers and books specifically authored by members of Coventry University’s School of Economics, Finance, and Accounting. The system crawls the relevant web pages and retrieves information about all available publications. For each publication, it extracts available data (such as authors, publication year, and title) and the links to both the publication page and the author's profile ("pureportal" profile) page.

### Task 2: Text Classification
This task involves creating a document classification system that can categorize texts into three distinct topics: Politics, Business, and Health. The system uses data extracted from New York Times in a csv file of 120 documents in each category.

#### **File Structure**
```
├── crawler.py          # Handles crawling and data extraction
├── indexer.py          # Builds and manages the inverted index
├── query_processor.py  # Processes user queries and displays results
├── utils.py            # Utility functions (e.g., text preprocessing)
├── selenium_setup.py   # Selenium web driver setup for web scraping
├── model_train.py      # Trains the Multinomial NB with the available dataset
├── app.py              # Streamlit app, main script to run the search engine and text classification based on three Categories: Politics, Business and Health
```


#### **How to Run**
1. **Clone the repository**:
   ```bash
   git clone https://github.com/Rashik2k/Search_Engine-and-Subject_Classification.git
   ```
2. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   streamlit run app.py
   ```
