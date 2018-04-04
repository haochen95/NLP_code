import scrapy
import re
from bs4 import BeautifulSoup
from construction.items import ConstructionItem

keywords = input ( 'Please enter Keyword ----->' )

class Construction(scrapy.Spider):
    # Run command :   scrapy crawl construction
    name = 'construction'  # must have a name to run this class
    domain = ['https://www.osha.gov/']   # limit operates only on this domain

    uu1 = 'https://www.osha.gov/pls/imis/accidentsearch.search?sic=&sicgroup=&naics=&acc_description=&acc_abstract=&acc_keyword='
    base_url1 = '&inspnr=&fatal=&officetype=All&office=All&startmonth=12&startday=31&startyear=2017&endmonth=01&endday=01&endyear=1984&keyword_list=&p_start=&p_finish='
    base_url2 = '&p_sort=&p_desc=DESC&p_direction=Next&p_show=20'
    offset = 0
    start_urls = [uu1 + keywords.replace(' ','').lower() + base_url1 + str(offset) + base_url2]

    # parse response and extract text from response (every response has one parse)
    def parse(self, response):
        sub_domain = 'https://www.osha.gov/pls/imis/'
        for tr in response.xpath('//table[@class = "table table-bordered table-striped"]/tr')[2:]:   # extract text from ('') which can be found using click button in your broswer.
            # transfer xpath to unicode strings ([] type)
            sub_url = sub_domain + tr.xpath('./td[3]/a/@href').extract()[0]
            # for each sub_url, open this url, receive response and build it's parse method
            yield scrapy.Request(sub_url, self.parse_detail)
        # Decide when to stop extract the sub_url (in this case, spider stops until it has no Next Page Options)
        if len(response.xpath('//a[@title = "Next Page"]/@href')) != 0:
            url = response.xpath('//a[@title = "Next Page"]/@href').extract()[0]
            yield scrapy.Request('https://www.osha.gov/pls/imis/' + url, callback=self.parse)

            # build up parse method for each response
    def parse_detail(self, response):
        item = ConstructionItem()
        item['address'] = response.request.url
        # from the sub_url, extract needed information (descriptions)
        info = response.xpath("//td[@colspan ='8' and not (contains(div, 't'))]/text()").extract()[0]  # extract
        text = (line.strip() for line in info.splitlines())
        s_text = '\n'.join(chunk for chunk in text if chunk)
        item['info'] = s_text
        yield item

