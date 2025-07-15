"""
測試爬蟲運行
Test Crawler Run
"""

from crawler.ctee_insurance_crawler import CTeeInsuranceCrawler
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)

def main():
    """測試工商時報爬蟲"""
    print("開始測試工商時報保險版爬蟲")
    
    crawler = CTeeInsuranceCrawler()
    result = crawler.crawl(max_pages=1, max_details=2)
    
    print(f"爬取完成：共 {len(result['news'])} 篇文章")
    
    for i, news in enumerate(result['news'][:2]):
        print(f"\n[{i+1}] {news['title']}")
        if 'published_date' in news:
            print(f"    日期: {news['published_date']}")
        print(f"    網址: {news['url']}")
        if 'content' in news:
            content_preview = news['content'][:100] + "..." if len(news['content']) > 100 else news['content']
            print(f"    內容預覽: {content_preview}")
    
    print("\n測試完成")

if __name__ == "__main__":
    main()
