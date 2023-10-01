'''
This is the main file that executes the program.
'''
from crawler import Crawler
def main():
    # Create an instance of the Crawler class
    crawler = Crawler()
    # Start the crawling process
    crawler.start()
if __name__ == "__main__":
    main()