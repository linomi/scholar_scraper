from bs4 import BeautifulSoup
import requests
import time
import json

class GoogleScholarScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.session = requests.Session()

    def scrape_profile(self, profile_url):        

        papers = []
        start = 0
                # Construct URL with pagination
        page_url = f"{profile_url}&cstart={start}&pagesize=100"
        response = self.session.get(page_url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"Failed to fetch page. Status code: {response.status_code}")
        soup = BeautifulSoup(response.content, "html.parser")
        self.person = soup.find('div',id='gsc_prf_in').text.strip()
        while True:
            try:
                # Construct URL with pagination
                page_url = f"{profile_url}&cstart={start}&pagesize=100"
                response = self.session.get(page_url, headers=self.headers)
                
                if response.status_code != 200:
                    print(f"Failed to fetch page. Status code: {response.status_code}")
                    break

                soup = BeautifulSoup(response.content, "html.parser")
                paper_items = soup.find_all("tr", class_="gsc_a_tr")
                
                if not paper_items:
                    break

                for item in paper_items:
                    try:
                        # Extract title
                        link_tag = item.find('a', class_='gsc_a_at')
                        full_link = 'https://scholar.google.com' + link_tag.get('href')
                        r = self.session.get(full_link,headers=self.headers)
                        so = BeautifulSoup(r.content, 'html.parser')
                        description = so.find('div',class_='gsh_small').text.strip()
                        


                        title_element = item.find("a", class_="gsc_a_at")
                        title = title_element.text.strip() if title_element else "N/A"
                        
                        # Extract authors and publication info (as description)
                        authors_element = item.find("div", class_="gs_gray")
                        publication_element = item.find_all("div", class_="gs_gray")
                        
                        authors = authors_element.text.strip() if authors_element else "N/A"
                        publication_info = publication_element[1].text.strip() if len(publication_element) > 1 else "N/A"
                        
                        # Extract year
                        year_element = item.find("td", class_="gsc_a_y")
                        year = year_element.text.strip() if year_element else "N/A"
                        
                        paper_info = {
                            "title": title,
                            "authors": authors,
                            "publication_info": publication_info,
                            "year": year,
                            "description":description
                        }
                        
                        papers.append(paper_info)
                        #print(f"Scraped: {title}")
                        if len(papers)>20:
                            break
                    
                    except Exception as e:
                        print(f"Error processing paper item: {e}")
                        continue

                # Check if there are more pages
                next_button = soup.find("button", {"aria-label": "Next"})
                if not next_button or "disabled" in next_button.get("class", []):
                    break

                # Move to next page
                start += 100
                # Add delay between pages
                time.sleep(2)
                
            except Exception as e:
                print(f"Error processing page: {e}")
                break

        return papers

    def save_to_json(self, papers,number:int,dir='./'):
        """Save scraped papers to JSON file"""
        with open(dir+str(number)+self.person, 'w', encoding='utf-8') as f:
            json.dump({'about / research interests / opinion':{}}, f, ensure_ascii=False, indent=2)
            json.dump(papers, f, ensure_ascii=False, indent=2)





def main():
    i = 0 
    dir = './'
    profile_url =str(input('please paste the scholar profile url:  '))
    profile_url[:profile_url.find('&view')]
    profile_url += '&view_op=list_works&sortby=pubdate'
    scraper = GoogleScholarScraper()
    papers= scraper.scrape_profile(profile_url)
    scraper.save_to_json(papers,number=i,dir=dir)
    print(f"\nTotal papers scraped: {len(papers)}")
    print("Results saved to papers.json")
       
if __name__ == "__main__":
    main()
    